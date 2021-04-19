/*************************************************************************/
/*									 */
/*  Copyright 2010 Rulequest Research Pty Ltd.				 */
/*									 */
/*  This file is part of Cubist GPL Edition, a single-threaded version	 */
/*  of Cubist release 2.07.						 */
/*									 */
/*  Cubist GPL Edition is free software: you can redistribute it and/or	 */
/*  modify it under the terms of the GNU General Public License as	 */
/*  published by the Free Software Foundation, either version 3 of the	 */
/*  License, or (at your option) any later version.			 */
/*									 */
/*  Cubist GPL Edition is distributed in the hope that it will be	 */
/*  useful, but WITHOUT ANY WARRANTY; without even the implied warranty	 */
/*  of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the	 */
/*  GNU General Public License for more details.			 */
/*									 */
/*  You should have received a copy of the GNU General Public License	 */
/*  (gpl.txt) along with Cubist GPL Edition.  If not, see		 */
/*									 */
/*      <http://www.gnu.org/licenses/>.					 */
/*									 */
/*************************************************************************/



/*************************************************************************/
/*									 */
/*	Main routine, Cubist						 */
/*	--------------------						 */
/*									 */
/*************************************************************************/


#include "defns.i"
#include "extern.i"

#include <sys/time.h>
#include <sys/resource.h>

#define SetOpt(V)	V = strtod(OptArg, &EndPtr);\
			if ( ! EndPtr || *EndPtr != '\00' ) break;\
			ArgOK = true
#define SetIOpt(V)	V = strtol(OptArg, &EndPtr, 10);\
			if ( ! EndPtr || *EndPtr != '\00' ) break;\
			ArgOK = true


int main(int Argc, char *Argv[])
/*  ----  */
{
    int			o;
    extern String	OptArg, Option;
    char		*EndPtr;
    Boolean		FirstTime=true, ArgOK;
    double		StartTime, SumCWt=0;
    FILE		*F;
    CaseNo		SaveMaxCase, i, NCWt=0;
    Attribute		Att;

    struct rlimit RL;

    /*  Make sure there is a largish runtime stack  */

    getrlimit(RLIMIT_STACK, &RL);

    RL.rlim_cur = Max(RL.rlim_cur, 20 * 1024 * 1024);

    if ( RL.rlim_max > 0 )	/* -1 if unlimited */
    {
	RL.rlim_cur = Min(RL.rlim_max, RL.rlim_cur);
    }

    setrlimit(RLIMIT_STACK, &RL);

    /*  Check for output to be saved to a file  */

    if ( Argc > 2 && ! strcmp(Argv[Argc-2], "-o") )
    {
	Of = fopen(Argv[Argc-1], "w");
	Argc -= 2;
    }

    if ( ! Of )
    {
	Of = stdout;
    }

    KRInit = time(0) & 07777;
    StartTime = ExecTime();
    PrintHeader("");

    /*  Process options  */

    while ( (o = ProcessOption(Argc, Argv, "f+v+r+e+ian+uS+I+X+C+h")) )
    {
	if ( FirstTime )
	{
	    fprintf(Of, T_OptHeader);
	    FirstTime = false;
	}

	ArgOK = false;

	switch (o)
	{
	case 'f':   FileStem = OptArg;
		    fprintf(Of, T_OptApplication, FileStem);
		    ArgOK = true;
		    break;
#ifdef VerbOpt
	case 'v':
		    VERBOSITY = atoi(OptArg);
		    fprintf(Of, "\tVerbosity level %d\n", VERBOSITY);
		    ArgOK = true;
		    break;
#endif
	case 'r':   SetIOpt(MAXRULES);
		    fprintf(Of, T_OptMaxRules, MAXRULES);
		    Check(MAXRULES, 1, 1000000);
		    break;
	case 'e':   SetOpt(EXTRAP);
		    fprintf(Of, T_OptExtrap, EXTRAP);
		    Check(EXTRAP, 0, 100);
		    EXTRAP /= 100;
		    break;
	case 'i':   USEINSTANCES = true;
		    fprintf(Of, T_OptUseInst);
		    ArgOK = true;
		    break;
	case 'a':   CHOOSEMODE = USEINSTANCES = true;
		    fprintf(Of, T_OptAllowInst);
		    ArgOK = true;
		    break;
	case 'n':   USEINSTANCES = true;
		    SetIOpt(NN);
		    fprintf(Of, TX_NNeighbors(NN));
		    Check(NN, 1, NNMAX);
		    ArgOK = true;
		    break;
	case 'u':   UNBIASED = true;
		    fprintf(Of, T_NoBias);
		    ArgOK = true;
		    break;
	case 'S':   SetOpt(SAMPLE);
	            fprintf(Of, T_OptSampling, SAMPLE);
	            Check(SAMPLE, 0.1, 99.9);
	            SAMPLE /= 100;
	            break;
	case 'I':   SetIOpt(KRInit);
		    fprintf(Of, T_OptSeed, KRInit);
		    KRInit = KRInit & 07777;
		    break;
	case 'X':   SetIOpt(FOLDS);
	            fprintf(Of, T_OptXval, FOLDS);
	            Check(FOLDS, 1, 1000);
		    XVAL = true;
	            break;
	case 'C':   SetIOpt(MEMBERS);
	            fprintf(Of, T_OptCttee, MEMBERS);
	            Check(MEMBERS, 1, 100);
	            break;
	}

	if ( ! ArgOK )
	{
	    if ( o != 'h' )
	    {
		fprintf(Of, T_UnregnizedOpt, Option,
			    ( ! OptArg || OptArg == Option+2 ? "" : OptArg ));
		fprintf(Of, T_SummaryOpts);
	    }
	    fprintf(Of, T_ListOpts);
	    Goodbye(1);
	}
    }

    /*  Get information on training data  */

    if ( ! (F = GetFile(".names", "r")) ) Error(NOFILE, "", "");
    GetNames(F);

    fprintf(Of, T_TargetAtt, AttName[ClassAtt]);
    
    NotifyStage(READDATA);
    Progress(-1.0);

    if ( ! (F = GetFile(".data", "r")) ) Error(NOFILE, "", "");
    GetData(F, true, false);
    fprintf(Of, TX_ReadData(MaxCase+1, MaxAtt, FileStem));

    if ( XVAL && (F = GetFile(".test", "r")) )
    {
	SaveMaxCase = MaxCase;
	GetData(F, false, false);
	fprintf(Of, TX_ReadTest(MaxCase-SaveMaxCase, FileStem));
    }

    /*  Check whether case weight attribute appears.  If it does,
	normalize values to average 1, and replace N/A values and
	values <= 0 with average value 1  */

    if ( CWtAtt )
    {
	fprintf(Of, T_CWtAtt);

	/*  Find average case weight value  */

	ForEach(i, 0, MaxCase)
	{
	    if ( ! NotApplic(Case[i], CWtAtt) && CVal(Case[i], CWtAtt) > 0 )
	    {
		SumCWt += CVal(Case[i], CWtAtt);
		NCWt += 1;
	    }
	}

	AvCWt = ( NCWt > 0 ? SumCWt / NCWt : 1 );

	ForEach(i, 0, MaxCase)
	{
	    if ( ! NotApplic(Case[i], CWtAtt) && CVal(Case[i], CWtAtt) > 0 )
	    {
		CVal(Case[i], CWtAtt) /= AvCWt;
	    }
	    else
	    {
		CVal(Case[i], CWtAtt) = 1;
	    }
	}
    }
    else
    {
	AvCWt = 1;
    }

    /*  Note any attribute exclusions/inclusions  */

    if ( AttExIn )
    {
	fprintf(Of, "%s", ( AttExIn == -1 ? T_AttributesOut : T_AttributesIn ));

	ForEach(Att, 1, MaxAtt)
	{
	    if ( ( StatBit(Att, SKIP) > 0 ) == ( AttExIn == -1 ) )
	    {
		fprintf(Of, "    %s\n", AttName[Att]);
	    }
	}
    }

    /*  Build and evaluate cubist model  */

    InitialiseEnvData();

    if ( XVAL )
    {
	CrossVal();
    }
    else
    {
	SingleCttee();
    }

#ifdef VerbOpt
    Cleanup();
#endif

    fprintf(Of, T_Time, ExecTime() - StartTime);

    return 0;
}
