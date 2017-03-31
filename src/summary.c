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
/*	Show summary of performance on test data			 */
/*	----------------------------------------			 */
/*									 */
/*************************************************************************/


#include <math.h>
#include <stdio.h>
#include <stdlib.h>


#define ForEach(v,f,l) for(v=f;v<=l;v++)
#define qsqrt(x) ((x)>0? sqrt((float) x): 0.0)
#define Plot(v) (Scale*(v-Base)+2)
#define Max(a,b) (a > b ? a : b)


/*************************************************************************/
/*									 */
/*	This is a specialised form of the getopt utility.		 */
/*									 */
/*************************************************************************/


char	*OptArg, *Option;


char ProcessOption(int Argc, char *Argv[], char *Options)
/*   -------------  */
{
    int		i;
    static int	OptNo=1;

    if ( OptNo >= Argc ) return '\00';

    if ( *(Option = Argv[OptNo++]) != '-' ) return '?';

    for ( i = 0 ; Options[i] ; i++ )
    {
	if ( Options[i] == Option[1] )
	{
	    OptArg = ( Options[i+1] != '+' ? 0 :
		       Option[2] ? Option+2 :
		       OptNo < Argc ? Argv[OptNo++] : "0" );
	    return Option[1];
	}
    }

    return '?';
}




int main(int Argc, char *Argv[])
/*  ----  */
{
    int		o;
    char	*FileStem=0, FileName[100], Msg[100], Show=1, Quit=0;
    FILE	*F;

    int		i, N=0, Size=0, Precision=0, Denom, Digits;
    float	*RVal, *PVal, MinRVal, MaxRVal, MinPVal, MaxPVal, Base, Scale,
		V, Mean, Real, Pred;
    double	SumX=0, SumY=0, SumXY=0, SumXX=0, SumYY=0,
		SumAbsErr=0, SumBaseAbsErr=0;
    char	Line[200], AvAbsErr[20], CorCoeff[20], RelErr[20];


    /*  Process options  */

    while ( (o = ProcessOption(Argc, Argv, "f+n")) )
    {
	switch (o)
	{
	case 'f':   sprintf(FileName, "%s.pred", OptArg);
		    FileStem = OptArg;
		    break;
	case 'n':   Show = 0;
		    break;
	case '?':   ; /* ignore illegal options  */
	}
    }


    /*  Open file containing output  */

    if ( ! FileStem )
    {
	sprintf(Msg, "Result file not specified");
	Quit = 1;
    }
    else
    if ( ! (F = fopen(FileName, "r")) )
    {
	sprintf(Msg, "Cannot open file %s", FileName);
	Quit = 1;
    }

    if ( Quit )
    {
	{
	    fprintf(stderr, "%s\n", Msg);
	}

	exit(1);
    }

    while ( fgets(Line, 200, F) )
    {
	if ( sscanf(Line, "(Default value %g", &Mean) == 1 )
	    ;
	else
	if ( sscanf(Line, "%f %f", &Real, &Pred) == 2 )
	{
	    if ( N >= Size )
	    {
		Size += 1000;
		if ( Size > 1000 )
		{
		    RVal = (float *) realloc(RVal, Size * sizeof(float));
		    PVal = (float *) realloc(PVal, Size * sizeof(float));
		}
		else
		{
		    RVal = (float *) malloc(Size * sizeof(float));
		    PVal = (float *) malloc(Size * sizeof(float));
		}
	    }

	    RVal[N] = Real;
	    PVal[N] = Pred;
	    N++;

	    SumAbsErr     += fabs(Real - Pred);
	    SumBaseAbsErr += fabs(Real - Mean);

	    SumX  += Real;
	    SumXX += Real * Real;
	    SumY  += Pred;
	    SumYY += Pred * Pred;
	    SumXY += Real * Pred;

	    /*  Determine max precision so far  */

	    V      = fabs(Real - rint(Real));
	    Denom  = 10000;
	    Digits = 4;
	    while ( Digits >= 0 &&
		    fabs(((int) (V * Denom + 0.5)) - V * Denom) < 0.1 )
	    {
		Denom /= 10;
		Digits--;
	    }

	    if ( Digits >= Precision ) Precision = Digits+1;
	}
    }
    fclose(F);

    /*  Compute summary statistics  */

    sprintf(AvAbsErr, "%.*f", Precision+1, SumAbsErr / N);
    sprintf(RelErr, "%.2f", SumAbsErr / SumBaseAbsErr);
    sprintf(CorCoeff, "%.2f",
		      ( SumXY - SumX * SumY / N ) /
			( qsqrt( (SumXX - SumX * SumX / N) *
			(SumYY - SumY * SumY / N) ) + 1E-6 ));

    /*  If not showing graph, print and quit  */

    if ( ! Show )
    {
	printf("Summary:\n--------\n\n");
	printf("    Average  |error|         %10.10s\n", AvAbsErr);
	printf("    Relative |error|               %4.4s\n", RelErr);
	printf("    Correlation coefficient        %s\n", CorCoeff);
	exit(0);
    }


    return 0;
}
