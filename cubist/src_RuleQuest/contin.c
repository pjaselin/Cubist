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
/*                                                                	 */
/*	Evaluation of a test on a continuous valued attribute	  	 */
/*	-----------------------------------------------------	  	 */
/*								  	 */
/*	Tests on continuous attributes have three possible		 */
/*	outcomes: 1 (N/A), 2 (less than cut), 3 (greater than cut).	 */
/*	This routine finds the best cut for items Fp through Lp and	 */
/*	sets GEnv.Gain[] and GEnv.Bar[].				 */
/*								  	 */
/*	For outcomes 2 and 3, we imagine a least-squares linear model	 */
/*	of the inputs as a function of the continuous attribute.	 */
/*	The residuals of each model have mean 0 and sum of squares	 */
/*	(1-R^2) * N * variance of the inputs where R is the correlation	 */
/*	coeff and N is the number of cases.  Note that these models	 */
/*	do not have to be found; all we need is the correl coeffs for	 */
/*	these outcomes.							 */
/*								  	 */
/*************************************************************************/


#include "defns.i"
#include "extern.i"


void EvalContinuousAtt(Tree Node, Attribute Att, CaseNo Fp, CaseNo Lp)
/*   -----------------  */ 
{ 
    CaseNo	i, Xp, BestI, Cases, Edge, LoK, HiK;
    ContValue	Val, LowVal, HighVal;
    double	ThisGain, BestGain=0,
    		LoSumX=0, LoSumXX=0, LoSumY=0, LoSumYY=0,
		LoSumXY=0, LoN, LoMX, LoVX, LoMY, LoVY, LoR,
    		HiSumX=0, HiSumXX=0, HiSumY=0, HiSumYY=0,
		HiSumXY=0, HiN, HiMX, HiVX, HiMY, HiVY, HiR,
		Wt, X, Exp2Z;

    /*  Lots of cryptic variable names!  Here's the key:
	Lo = outcome 2, Hi = outcome 3
	X = attribute value, Y = input value (i.e., target residual)
	M = mean, V = variance
	N = weighted number of cases, K = count
	R = correlation coefficient  */

    /*  Special case when very few values  */

    if ( (Cases = Lp - Fp + 1) < 2 * MINSPLIT )
    {
	Verbosity(2, fprintf(Of, "Att %s\tinsufficient cases\n", AttName[Att]) )

	return;
    }

    GEnv.BrSum[1] = GEnv.BrSumSq[1] = GEnv.BrFreq[1] =
    GEnv.BrSum[2] = GEnv.BrSumSq[2] = GEnv.BrFreq[2] =
    GEnv.BrSum[3] = GEnv.BrSumSq[3] = GEnv.BrFreq[3] = 0;

    /*  Isolate N/A values and sort the rest on the attribute value.
	All cases are initially assigned to the high branch (outcome 3)  */

    Xp = Lp+1;
    for ( i = Lp ; i >= Fp ; i-- )
    {
	Val = Resid(Case[i]);
	Wt  = CWeight(Case[i]);

	if ( NotApplic(Case[i], Att) )
	{
	    GEnv.BrSum[1]   += Wt * Val;
	    GEnv.BrSumSq[1] += Wt * Val * Val;
	    GEnv.BrFreq[1]  += Wt;
	}
	else
	{
	    X = CVal(Case[i], Att);

	    Xp--;
	    SRec[Xp].V = X;
	    SRec[Xp].T = Val;
	    SRec[Xp].W = Wt;

	    HiSumX  += Wt * X;
	    HiSumXX += Wt * X * X;
	    HiSumY  += Wt * Val;
	    HiSumYY += Wt * Val * Val;
	    HiSumXY += Wt * X * Val;

	    GEnv.BrFreq[3]  += Wt;
	}
    }

    Cachesort(Xp, Lp);

    /*  Try possible cuts between items i and i+1 and determine the
	gain of the split in each case  */

    Edge = (Cases >= 3 * MINITEMS ? MINITEMS : MINSPLIT );

    ForEach(i, Xp, Lp - Edge)
    {
	X   = SRec[i].V;
	Val = SRec[i].T;
	Wt  = SRec[i].W;

	GEnv.BrFreq[2] += Wt;
	GEnv.BrFreq[3] -= Wt;

	LoSumX  += Wt * X;
	LoSumXX += Wt * X * X;
	LoSumY  += Wt * Val;
	LoSumYY += Wt * Val * Val;
	LoSumXY += Wt * X * Val;
	HiSumX  -= Wt * X;
	HiSumXX -= Wt * X * X;
	HiSumY  -= Wt * Val;
	HiSumYY -= Wt * Val * Val;
	HiSumXY -= Wt * X * Val;

	if ( SRec[i+1].V > SRec[i].V && i >= Xp + Edge - 1 )
	{
	    /*  Possible cut here  */

	    LoK  = i - Xp + 1;
	    LoN  = GEnv.BrFreq[2];
	    LoMX = LoSumX / LoN;
	    LoVX = LoSumXX / LoN - LoMX * LoMX;
	    LoMY = LoSumY / LoN;
	    LoVY = LoSumYY / LoN - LoMY * LoMY;
	    LoR  = (LoSumXY - LoSumX * LoSumY / LoN) /
		   (LoN * sqrt(LoVX * LoVY + 1E-10));
	    Exp2Z =  ( LoK < 6 ? 1E38 : exp(2 * 1.96 * sqrt(1.0 / (LoK - 3))) );
	    if ( fabs(LoR) < (Exp2Z - 1) / (Exp2Z + 1) ) LoR = 0;

	    HiK  = Lp - i;
	    HiN  = GEnv.BrFreq[3];
	    HiMX = HiSumX / HiN;
	    HiVX = HiSumXX / HiN - HiMX * HiMX;
	    HiMY = HiSumY / HiN;
	    HiVY = HiSumYY / HiN - HiMY * HiMY;
	    HiR  = (HiSumXY - HiSumX * HiSumY / HiN) /
		   (HiN * sqrt(HiVX * HiVY + 1E-10));
	    Exp2Z =  ( HiK < 6 ? 1E38 : exp(2 * 1.96 * sqrt(1.0 / (HiK - 3))) );
	    if ( fabs(HiR) < (Exp2Z - 1) / (Exp2Z + 1) ) HiR = 0;

	    /*  Record the sums of squares of the imagined residuals  */

	    GEnv.BrSumSq[2] = (1 - LoR * LoR) * LoN * LoVY;
	    GEnv.BrSumSq[3] = (1 - HiR * HiR) * HiN * HiVY;

	    if ( (ThisGain = ComputeGain(Node)) > BestGain )
	    {
		BestGain = ThisGain;
		BestI    = i;
	    }
	}
    }

    /*  If there is a gain, set the best cut  */

    if ( BestGain > 0 )
    {
	GEnv.Gain[Att] = BestGain;

	LowVal  = SRec[BestI].V;
	HighVal = SRec[BestI+1].V;

	/*  Set threshold, making sure that rounding problems do not
	    cause it to reach upper value  */

	if ( (GEnv.Bar[Att] = (ContValue) (0.5 * (LowVal + HighVal))) >= HighVal )
	{
	    GEnv.Bar[Att] = LowVal;
	}

	Verbosity(2,
	    fprintf(Of, "Att %s\tcut=%.3f, gain %.3f\n",
			AttName[Att], GEnv.Bar[Att], GEnv.Gain[Att]))
    }
    else
    {
	GEnv.Gain[Att] = None;

	Verbosity(2, fprintf(Of, "Att %s\tno gain\n", AttName[Att]))
    }
} 



/*************************************************************************/
/*                                                                	 */
/*	Change a leaf into a test on a continuous attribute           	 */
/*                                                                	 */
/*************************************************************************/


void ContinTest(Tree Node, Attribute Att, float Cut)
/*   ----------  */
{
    Sprout(Node, 3);

    Node->NodeType	= BrThresh;
    Node->Tested	= Att;
    Node->Cut		= Cut;
}



/*************************************************************************/
/*                                                                	 */
/*	Adjust thresholds of all continuous attributes so that cut	 */
/*	values appear in the data					 */
/*                                                                	 */
/*************************************************************************/


Boolean	Sorted;


void AdjustAllThresholds(Tree T)
/*   -------------------  */
{
    Attribute	Att;

    ForEach(Att, 1, MaxAtt)
    {
	if ( Continuous(Att) )
	{
	    Sorted = false;
	    AdjustThresholds(T, Att);
	}
    }
}



void AdjustThresholds(Tree T, Attribute Att)
/*   ----------------  */
{
    DiscrValue	v;
    CaseNo	i;

    if ( T->NodeType == BrThresh && T->Tested == Att )
    {
	if ( ! Sorted )
	{
	    /*  Sort the attribute values.  Leaving N/A values doesn't
		matter since N/A will not lie between two real values  */

	    ForEach(i, 0, MaxCase)
	    {
		SRec[i].V = CVal(Case[i], Att);
	    }

	    Cachesort(0, MaxCase);
	    Sorted = true;
	}

	T->Cut = GreatestValueBelow(T->Cut);
    }

    if ( T->NodeType )
    {
	ForEach(v, 1, T->Forks)
	{
	    AdjustThresholds(T->Branch[v], Att);
	}
    }
}



/*************************************************************************/
/*                                                                	 */
/*	Return the greatest value of attribute Att below threshold Th. 	 */
/*	(Assumes values of Att have been sorted in SRec.)		 */
/*                                                                	 */
/*************************************************************************/


ContValue GreatestValueBelow(ContValue Th)
/*	  ------------------  */
{
    CaseNo	Low, High, Mid;

    Low = 0;
    High = MaxCase;

    while ( Low < High )
    {
	Mid = (Low + High + 1) / 2;

	if ( SRec[Mid].V > Th )
	{
	    High = Mid - 1;
	}
	else
	{
	    Low = Mid;
	}
    }

    return SRec[Low].V;
}
