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



#include "defns.i"
#include "extern.i"

double	TotalErr, ExtraErr, TotalParams, ExtraParams, AdjErrLim, NewAdjErr;

Tree	Weakest;
#define	ResidWt	PResid



/*************************************************************************/
/*									 */
/*	Simplify tree T by successively pruning the weakest subtree.	 */
/*									 */
/*	Repeat								 */
/*	 * examine each subtree of T to find the effect on global error	 */
/*	   and number of parameters if subtree pruned			 */
/*	 * if there is one with lower estimated error, prune the subtree */
/*	   that introduces least additional error			 */
/*									 */
/*	Then, prune a little further.					 */
/*									 */
/*	For each subtree S, S->Utility gives the minimum additional	 */
/*	error obtainable by pruning S or any of its subtrees.  This	 */
/*	is used to eliminate candidates for weakest subtree.		 */
/*									 */
/*************************************************************************/


void Prune(Tree T)
/*   -----  */
{
    double	AdjErr;
    int		Leaves, Stage=1;


    /*  Calculate numbers of parameters and coefficients  */

    SetProperties(T, Nil);

    /*  Models must be smoothed first so that error at each node
	can be determined directly  */

    Verbosity(1, PrintTree(T, "Initial model tree"))

    SmoothModels(T, Nil, 0, MaxCase);

    FindErrors(T, 0, MaxCase);

    Leaves = TreeLeaves(T);

    /*  Pruning is carried out in three stages.  In the first stage, we
	find a sequence of trees with non-increasing adjusted error.
	The second stage allows adjusted error to increase by 0.5%,
	yielding simpler models.  In the final stage, pruning continues
	until the number of leaves does not exceed MAXRULES  */

    while ( true )
    {
	TotalParams = T->Params;
	TotalErr    = T->TreeErr;

	AdjErr  = (MaxCase+1) * EstimateErr(TotalErr / (MaxCase+1.0),
						MaxCase+1, TotalParams);
	if ( Stage == 1 ) AdjErrLim = AdjErr;

	Verbosity(1,
	    fprintf(Of, "\n(%g params, %d leaves)"
			" total actual/est err %.1f/%.1f\n",
		   	TotalParams, Leaves, TotalErr, AdjErr))

	ExtraErr = 1E38;	/* initialise minimum extra error */

	if ( FindWeakestSubtree(T) &&
	     ( NewAdjErr <= AdjErr || Stage > 1 ) )
	{
	    Leaves -= TreeLeaves(Weakest) - 1;
	    UnsproutAndUpdate(Weakest, ExtraErr, ExtraParams);
	}
	else
	if ( Stage == 1 )
	{
	    Stage = 2;
	    AdjErrLim = AdjErr * 1.005;
	}
	else
	{
	    Stage = 3;
	    AdjErrLim = 1E38;
	}

	if ( Stage == 3 && Leaves <= MAXRULES ) break;
    }
}





/*************************************************************************/
/*									 */
/*	Set Params and Coeffs for tree T.  (Params currently holds	 */
/*	the parameters equivalent of each test, but we need the		 */
/*	totals including subtrees.)					 */
/*									 */
/*	Also remove any subtrees that have very small branches		 */
/*									 */
/*************************************************************************/


void SetProperties(Tree T, Tree Parent)
/*   -------------  */
{
    DiscrValue	v;

    /*  Eliminate any branches that cover too few cases  */

    if ( T->NodeType &&
	 ( T->Branch[2]->Cases < MINITEMS ||
	   T->Branch[3]->Cases < MINITEMS ) )
    {
	Unsprout(T);
    }

    if ( T->Coeffs )
    {
	T->Coeffs = 0.5 * (T->Coeffs + CountCoeffs(T->Model));
    }
    else
    {
	T->Coeffs = CountCoeffs(T->Model);
    }

    if ( T->NodeType )
    {
	Parent(T) = Parent;

	T->MCopy = Alloc(MaxAtt+1, double);
	memcpy(T->MCopy, T->Model, (MaxAtt+1) * sizeof(double));

	if ( Discrete(T->Tested) )
	{
	    T->Params = ( T->NodeType == BrSubset ? 4 : 3 );
	}
	else
	{ 
	    T->Params = 4;
	} 

	ForEach(v, 1, T->Forks)
	{
	    if ( T->Branch[v]->Cases > 0 )
	    {
		SetProperties(T->Branch[v], T);
		T->Params += T->Branch[v]->Params;
	    }
	}
    }
    else
    {
	T->Params = T->Coeffs;
    }
}



/*************************************************************************/
/*									 */
/*	Replace a subtree by a leaf and adjust properties		 */
/*									 */
/*************************************************************************/


void UnsproutAndUpdate(Tree Pruned, double ExtraErr, double ExtraParams)
/*   -----------------  */
{
    DiscrValue	v;
    Tree	T;
    double	MinExtraErr=1E38;

    Pruned->Utility  = 1E38;

    for ( T = Pruned ; T ; T = Parent(T) )
    {
	T->TreeErr += ExtraErr;
	T->Params  += ExtraParams;

	if ( T != Pruned )
	{
	    ForEach(v, 1, T->Forks)
	    {
		if ( T->Branch[v]->Utility < MinExtraErr )
		{
		    MinExtraErr = T->Branch[v]->Utility;
		}
	    }

	    T->Utility = Min(MinExtraErr, T->LeafErr - T->TreeErr);
	}
    }

    Unsprout(Pruned);
}



/*************************************************************************/
/*									 */
/*	Replace a subtree by a leaf					 */
/*									 */
/*************************************************************************/


void Unsprout(Tree T)
/*   --------  */
{
    DiscrValue	v;

    Progress(TreeSize(T)-1);

    Verbosity(1, PrintTree(T, "Prune subtree"))

    /*  Free subtrees etc  */

    ForEach(v, 1, T->Forks)
    {
	FreeTree(T->Branch[v]);
    }
    Free(T->Branch);				T->Branch = Nil;

    if ( T->NodeType == BrSubset )
    {
	FreeVector((void **) T->Subset, 1, 3);	T->Subset = Nil;
    }

    T->NodeType = 0;
}



/*************************************************************************/
/*									 */
/*	Use Pregibon-like "shrinking" to smooth all models and		 */
/*	simplify model coefficients					 */
/*									 */
/*************************************************************************/


void SmoothModels(Tree T, Tree Parent, CaseNo Fp, CaseNo Lp)
/*   ------------  */
{
    DiscrValue	v;
    Attribute	Att;
    CaseNo	i, Bp;
    CaseCount	Cases;
    double	Wt, SumWt, SumX, SumY, SumXY, Cov,
		CurrVar, ParentVar, pCurr; 

    /*  Smooth models at subtrees  */

    if ( T->NodeType )
    {
	Bp = Fp;
	ForEach(v, 1, T->Forks)
	{
	    if ( (Cases = T->Branch[v]->Cases) > 0 )
	    {
		SmoothModels(T->Branch[v], T, Bp, Bp + Cases - 1);
		Bp += Cases;
	    }
	}
    }

    /*  Ignore smoothing if no variation in target or if sum of case
	weights is small */

    if ( CWtAtt )
    {
	SumWt = 0;
	ForEach(i, Fp, Lp)
	{
	    SumWt += CWeight(Case[i]);
	}
    }
    else
    {
	SumWt = Lp-Fp+1;
    }

    /*  Save errors of model in GEnv.Resid and compute variance  */

    CurrVar = ErrVariance(T->Model, Fp, Lp, GEnv.Resid);

    if ( SumWt > 2 && CurrVar > 1E-10 )
    {

	for ( ; Parent ; Parent = Parent(Parent) )
	{
	    /*  Save errors of parent in GEnv.PResid and find variance  */

	    ParentVar = ErrVariance(Parent->MCopy, Fp, Lp, GEnv.PResid);

	    /*  Determine best combination of parent and current models
		to minimise error variance.  Smoothed model is
		    pCurr * model + (1-pCurr) * parent model
		Minimisation requires covariance of error values  */

	    SumX = SumY = SumXY = 0;
	    ForEach(i, Fp, Lp)
	    {
		Wt = CWeight(Case[i]);

		SumX  += Wt * GEnv.Resid[i];
		SumY  += Wt * GEnv.PResid[i];
		SumXY += Wt * GEnv.Resid[i] * GEnv.PResid[i];
	    }
	    Cov = (SumXY - SumX * SumY / SumWt) / (SumWt - 1);

	    pCurr = ( CurrVar + ParentVar - 2 * Cov <= 1E-12 ? 1 :
	    	       (ParentVar - Cov) / (CurrVar + ParentVar - 2 * Cov) );

	    /*  Form smoothed model, if sensible, and recompute model
		errors and error variance  */

	    if ( pCurr > 0 && pCurr < 1 )
	    {
		ForEach(Att, 0, MaxAtt)
		{
		    T->Model[Att] = T->Model[Att] * pCurr +
				    Parent->MCopy[Att] * (1 - pCurr);
		}
		CurrVar = ErrVariance(T->Model, Fp, Lp, GEnv.Resid);
	    }
	}
    }

    /*  Simplify coefficients using AttUnit  */

    ForEach(Att, 1, MaxAtt)
    {
	if ( T->Model[Att] )
	{
	    T->Model[Att] =
		( fabs(T->Model[Att]) < MinAttCoeff(Att) ? 0 :
		      rint(T->Model[Att] / AttUnit[Att]) * AttUnit[Att] );
	}
    }

    /*  Adjust intercept so that weighted median error is zero and simplify  */

    FindModelAtts(T->Model);

    ForEach(i, Fp, Lp)
    {
	GEnv.Resid[i] = RawLinModel(T->Model, Case[i]) - Class(Case[i]);
	GEnv.ResidWt[i] = CWeight(Case[i]);
    }
    T->Model[0] -= MedianResid(Fp, Lp, SumWt / 2);

    T->Model[0] = rint(T->Model[0] / AttUnit[0]) * AttUnit[0];
}



/*************************************************************************/
/*									 */
/*	Save error on each case and compute variance			 */
/*									 */
/*************************************************************************/


double ErrVariance(double *Model, CaseNo Fp, CaseNo Lp, double *Err)
/*     -----------  */
{
    double	V, SumWt=0, Sum=0, SumSq=0, Wt, Var;
    CaseNo	i;

    FindModelAtts(Model);

    ForEach(i, Fp, Lp)
    {
	Err[i] = V = Class(Case[i]) - LinModel(Model, Case[i]);

        Wt = CWeight(Case[i]);

        SumWt += Wt;
	Sum   += Wt * V;
	SumSq += Wt * V * V;
    }

    return ( SumWt <= 1 ? 1E-38 :
	     (Var = (SumSq - Sum * Sum / SumWt) / (SumWt - 1)) > 1E-38 ? Var :
	     1E-38 );
}



/*************************************************************************/
/*									 */
/*	Find current error associated with each subtree and minimum	 */
/*	extra error if any sub-subtree is pruned			 */
/*									 */
/*************************************************************************/


void FindErrors(Tree T, CaseNo Fp, CaseNo Lp)
/*   ----------  */
{
    CaseNo	i, Bp, Cases;
    double	Wt, Err=0, MinExtraErr=1E38;
    DiscrValue	v;

    FindModelAtts(T->Model);

    ForEach(i, Fp, Lp)
    {
	Wt   = CWeight(Case[i]);
	Err += Wt * fabs(Class(Case[i]) - RawLinModel(T->Model, Case[i]));
    }
    T->LeafErr = T->TreeErr = Err;
    T->Utility = 1E38;

    if ( ! T->NodeType ) return;

    T->TreeErr = 0;
    Bp = Fp;
    ForEach(v, 1, T->Forks)
    {
	if ( (Cases = T->Branch[v]->Cases) > 0 )
	{
	    FindErrors(T->Branch[v], Bp, Bp + Cases - 1);
	    T->TreeErr += T->Branch[v]->TreeErr;

	    if ( T->Branch[v]->NodeType &&
		 T->Branch[v]->Utility < MinExtraErr )
	    {
		MinExtraErr = T->Branch[v]->Utility;
	    }

	    Bp += Cases;
	}
    }

    T->Utility = Min(MinExtraErr, T->LeafErr - T->TreeErr);
}



/*************************************************************************/
/*									 */
/*	Find "weakest" subtree in tree, defined as subtree that can	 */
/*	be deleted with least increase in actual error while keeping	 */
/*	adjusted error below AdjErrLim					 */
/*									 */
/*************************************************************************/


Boolean FindWeakestSubtree(Tree T)
/*      ------------------  */
{
    Boolean	Found=false;
    double	ThisExtraErr, ThisAdjErr;
    float	ThisExtraParams;
    DiscrValue	v;

    if ( ! T->NodeType ) return false;

    /*  Is this the weakest so far?  */

    ThisExtraErr    = T->LeafErr - T->TreeErr;
    ThisExtraParams = T->Coeffs - T->Params;

    ThisAdjErr = (MaxCase+1) *
		     EstimateErr((ThisExtraErr + TotalErr) / (MaxCase+1.0),
				 MaxCase+1, (ThisExtraParams + TotalParams));

    if ( ThisAdjErr <= AdjErrLim && ThisExtraErr < ExtraErr )
    {
	Weakest     = T;
	ExtraErr    = ThisExtraErr;
	ExtraParams = ThisExtraParams;
	NewAdjErr   = ThisAdjErr;
	Found	    = true;
    }

    /*  Check subtrees that could be weaker than current best  */

    ForEach(v, 1, T->Forks)
    {
	if ( T->Branch[v]->Utility <= ExtraErr )
	{
	    Found |= FindWeakestSubtree(T->Branch[v]);
	}
    }

    return Found;
}



/*************************************************************************/
/*									 */
/*	Compute predicted value from model at node			 */
/*									 */
/*************************************************************************/


float TreeValue(Tree T, DataRec Case)
/*    ---------  */
{ 
    DiscrValue	v, f;
    double	Val;
    Attribute	Att;

    Att = T->Tested;

    switch ( T->NodeType )
    {
	case 0:  /* leaf */

	    break;

	case BrDiscr:  /* test of discrete attribute */

	    v = DVal(Case, Att);

	    if ( v && v <= T->Forks && T->Branch[v]->Cases >= 1 )
	    {
		return TreeValue(T->Branch[v], Case);
	    }
	    else
	    {
		break;
	    }

	case BrThresh:  /* test of continuous attribute */

	    v = ( NotApplic(Case, Att) ? 1 :
		  CVal(Case, Att) <= T->Cut ? 2 : 3 );

	    return TreeValue(T->Branch[v], Case);

	case BrSubset:  /* subset test on discrete attribute  */

	    v = DVal(Case, Att);
	    f = ( v == 1 ? 1 : In(v, T->Subset[2]) ? 2 : 3 );

	    return TreeValue(T->Branch[f], Case);
    } 

    /*  Calculate value at this node.  Cannot use LinModel()  */

    Val = T->Model[0];
    ForEach(Att, 1, MaxAtt)
    {
	Val += CVal(Case, Att) * T->Model[Att];
    }

    return ( Val < Floor ? Floor : Val > Ceiling ? Ceiling : Val );
}



/*************************************************************************/
/*									 */
/*	Find median of residuals of cases in GEnv.Filtered.		 */
/*	Want initially contains half of the weight of cases Fp..Lp	 */
/*									 */
/*************************************************************************/

#define	 MSwap(a,b)	{Hold = GEnv.Resid[a];\
			 GEnv.Resid[a] = GEnv.Resid[b];\
			 GEnv.Resid[b] = Hold;\
			 Hold = GEnv.ResidWt[a];\
			 GEnv.ResidWt[a] = GEnv.ResidWt[b];\
			 GEnv.ResidWt[b] = Hold;}

float MedianResid(CaseNo Fp, CaseNo Lp, double Want)
/*    -----------  */
{
    CaseNo      i, Middle, High;
    double	LowWt, MiddleWt, Hold, Thresh, Val;

    while ( Fp < Lp )
    {
	Thresh = GEnv.Resid[(Fp+Lp) / 2];

	/*  Divide cases into three groups:
		Fp .. Middle-1: values < Thresh
		Middle .. High: values = Thresh
		High+1 .. Lp:   values > Thresh  */

	LowWt = MiddleWt = 0;

	for ( Middle = Fp ; GEnv.Resid[Middle] < Thresh ; Middle++ )
	{
	    LowWt += GEnv.ResidWt[Middle];
	}

	for ( High = Lp ; GEnv.Resid[High] > Thresh ; High-- )
	    ;

	for ( i = Middle ; i <= High ; )
	{
	    if ( (Val = GEnv.Resid[i]) < Thresh )
	    {
		LowWt += GEnv.ResidWt[i];
		MSwap(i, Middle);
		Middle++;
		i++;
	    }
	    else
	    if ( Val > Thresh )
	    {
		MSwap(i, High);
		High--;
	    }
	    else
	    {
		MiddleWt += GEnv.ResidWt[i];
		i++;
	    }
	}

	if ( Want <= LowWt )
	{
	    Lp = Middle-1;
	}
	else
	if ( Want > LowWt + MiddleWt )
	{
	    Want -= LowWt + MiddleWt;
	    Fp = High+1;
	}
	else
	{
	    return Thresh;
	}
    }

    return GEnv.Resid[Fp];
}
