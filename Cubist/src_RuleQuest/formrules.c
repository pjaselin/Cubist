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
/*								  	 */
/*	Form a set of rules from a model tree				 */
/*	-------------------------------------				 */
/*								  	 */
/*	The cases are partitionen into sublists:			 */
/*	  * Fail0: those cases that satisfy all undeleted conditions	 */
/*	  * Fail1: those that satisfy all but one of the above		 */
/*	  * FailMany: the remaining cases				 */
/*	Lists are implemented via Succ; Succ[i] is the number of the	 */
/*	case that follows case i.					 */
/*								  	 */
/*************************************************************************/


#include "defns.i"
#include "extern.i"

double		*Total=Nil,		/* [Condition] */
		*PredErr=Nil,		/* [Condition] */
		*Model;

Boolean		**CondFailedBy=Nil,	/* [Condition][CaseNo] */
		*Deleted=Nil;		/* [Condition] */

Condition	*Stack=Nil;

int		Leaves,
		MaxDepth,
		NCond,
		Bestd;

short		*NFail=Nil,		/* NFail[i] = conditions failed by i */
		*LocalNFail=Nil;	/* copy used during rule pruning */

CaseNo		*Succ=Nil,		/* case following case i */
		Fail0,			/* first satisfying all conditions */
		Fail1,			/* ditto all but one */
		FailMany;		/* first case failing 2+ conditions */

float		*CPredVal=Nil;		/* raw model values for each case */


RRuleSet FormRules(Tree T)
/*	 ---------  */
{
    CaseNo	i;
    RRuleSet	RS;

    /*  Record values predicted by tree  */

    ForEach(i, 0, MaxCase)
    {
	PredSum(Case[i])   = TreeValue(T, Case[i]);
	PredCount(Case[i]) = 1;
    }

    /*  Find essential parameters and allocate storage  */

    MaxDepth = Leaves = 0;

    TreeParameters(T, 0);

    Total        = Alloc(MaxDepth+2, double);
    PredErr      = Alloc(MaxDepth+2, double);

    CondFailedBy = AllocZero(MaxDepth+2, Boolean *);
    Deleted      = AllocZero(MaxDepth+2, Boolean);

    Stack        = AllocZero(MaxDepth+2, Condition);

    ForEach(i, 0, MaxDepth+1)
    {
	CondFailedBy[i] = AllocZero(MaxCase+1, Boolean);
    }

    NFail      = AllocZero(MaxCase+1, short);
    LocalNFail = AllocZero(MaxCase+1, short);

    Succ       = Alloc(MaxCase+1, CaseNo);

    NRules = RuleSpace = 0;

    CPredVal = Alloc(MaxCase+1, float);

    /*  Extract and prune paths from root to leaves  */

    NCond = 0;
    Scan(T);

    OrderRules();

    RS = Alloc(1, RuleSetRec);

    RS->SNRules  = NRules;
    RS->SRule    = Rule;				Rule = Nil;

    /*  Deallocate storage  */

    FreeFormRuleData();

    return RS;
}



/*************************************************************************/
/*                                                                	 */
/*	Find the maximum depth and the number of leaves in tree T  	 */
/*	with initial depth D					  	 */
/*                                                                	 */
/*************************************************************************/


void TreeParameters(Tree T, int D)
/*   --------------  */
{
    DiscrValue	v;

    if ( T->NodeType )
    {
	ForEach(v, 1, T->Forks)
	{
	    TreeParameters(T->Branch[v], D+1);
	}
    }
    else
    {
	Leaves++;
	if ( D > MaxDepth ) MaxDepth = D;
    }
}



/*************************************************************************/
/*								  	 */
/*	Extract paths from tree T at depth D, and process them  	 */
/*								  	 */
/*************************************************************************/


void Scan(Tree T)
/*   ----  */
{
    DiscrValue	v;
    Condition	Term;

    if ( T->NodeType )
    {
	NCond++;

	Term = AllocZero(1, CondRec);

	Term->NodeType = T->NodeType;
	Term->Tested   = T->Tested;
	Term->Cut      = T->Cut;

	Stack[NCond] = Term;

	ForEach(v, 1, T->Forks)
	{
	    Stack[NCond]->TestValue = v;
	    if ( Term->NodeType == BrSubset ) Term->Subset = T->Subset[v];

	    /*  Adjust number of failed conditions  */

	    PushCondition();

	    Scan(T->Branch[v]);

	    /*  Reset number of failed conditions  */

	    PopCondition();
	}

	/*  Free local storage  */

	Free(Term);

	NCond--;
    }
    else
    if ( T->Cases >= 1 )
    {
	memcpy(LocalNFail, NFail, (MaxCase+1) * sizeof(short));

	/*  Prune the current path  */

	Model = T->Model;
	PruneRule(Stack, T->Coeffs);

	if ( ! T->NodeType ) Progress((float) T->Cases);
    }
}



/*************************************************************************/
/*								  	 */
/*	Update NFail when a condition is added to/removed from Stack	 */
/*								  	 */
/*************************************************************************/


void PushCondition()
/*   -------------  */
{
    int i;

    ForEach(i, 0, MaxCase)
    {
	if ( (CondFailedBy[NCond][i] = ! Satisfies(Case[i], Stack[NCond])) )
	{
	    NFail[i]++;
	}
    }
}



void PopCondition()
/*   -------------  */
{
    int i;

    ForEach(i, 0, MaxCase)
    {
	if ( CondFailedBy[NCond][i] )
	{
	    NFail[i]--;
	}
    }
}



/*************************************************************************/
/*									 */
/*	Prune the rule given by the conditions Cond, and the number of	 */
/*	conditions NCond, and add the resulting rule to the current	 */
/*	ruleset if it is sufficiently accurate				 */
/*									 */
/*************************************************************************/


void PruneRule(Condition Cond[], float InitCoeffs)
/*   ---------  */
{
    int		d, id, Bestid, Remaining=NCond;
    ContValue	Val, LoVal=1E38, HiVal=-1E38, Wt;
    double	Sum=0, SumWt=0;
    CaseNo	i;
    CaseCount	Cover=0;

    FindModelAtts(Model);

    Bestd = 0;

    ForEach(d, 0, NCond)
    {
	Deleted[d] = false;
    }

    /*  Find conditions to delete  */

    Verbosity(1, fprintf(Of, "\n  Pruning rule"))

    while ( true )
    {
	/*  Initialise or update fail lists, totals, and predicted errors  */

	ProcessLists();

	if ( Remaining == 1 ) break;

	/*  See whether a condition can be deleted  */

	Bestd = id = 0;

	Verbosity(1,
	    fprintf(Of, "\n      Used   Err \tAbsent condition\n"))

	ForEach(d, 0, NCond)
	{
	    if ( Deleted[d] ) continue;

	    Verbosity(1,
		fprintf(Of, "   %7g%7.1f",
			    rint(Total[d] * 10) / 10, PredErr[d]))

	    if ( ! d )
	    {
		Verbosity(1, fprintf(Of, "\t<base rule>\n"))
	    }
	    else
	    {
		id++;

		Verbosity(1, PrintCondition(Cond[d]))

		/*  Bestd identifies the condition whose removal would
		    lead to the greatest improvement in the newly-covered
		    cases  */

		if ( PredErr[d] >= 0 &&
		     ( ! Bestd || PredErr[d] > PredErr[Bestd] ) )
		{
		    Bestd  = d;
		    Bestid = id;
		}
	    }
	}

 	if ( ! Bestd ) break;

	Verbosity(1, fprintf(Of, "\teliminate test %d\n", Bestid))

	Deleted[Bestd] = true;
	Remaining--;
    }

    /*  Check whether pruned rule is viable  */

    if ( NCond && ! Remaining ) return;

    /*  Find lowest and highest value among cases covered by this rule,
	and the average local error  */

    for ( i = Fail0 ; i >= 0 ; )
    {
	Cover++;

	Wt     = CWeight(Case[i]);
	SumWt += Wt;
	Sum   += Wt * (Val = Class(Case[i]));

	LoVal = Min(LoVal, Val);
	HiVal = Max(HiVal, Val);

	i = Succ[i];
    }

    /*  Add this as a possible new rule  */

    PredErr[0] = EstimateErr(PredErr[0]/Total[0], Cover, InitCoeffs);

    if ( NewRule(Cond, NCond, Deleted, Cover, Sum / SumWt, LoVal, HiVal,
	    PredErr[0], Model) )
    {
	/*  Adjust average predictions for new cases covered by this rule.
	    Do not adjust for cases covered by the initial rule, since the
	    value was entered at initialisation  */

	for ( i = Fail0 ; i >= 0 ; )
	{
	    if ( NFail[i] )	/* not covered by initial rule */
	    {
		PredSum(Case[i]) += ( CPredVal[i] < LoVal ? LoVal :
				      CPredVal[i] > HiVal ? HiVal :
				      CPredVal[i] );
		PredCount(Case[i])++;
	    }

	    i = Succ[i];
	}

	if ( UNBIASED ) RemoveBias(Rule[NRules], InitCoeffs);
    }
}



/*************************************************************************/
/*									 */
/*	Increment counts and averages					 */
/*									 */
/*************************************************************************/


void UpdateCount(int d, CaseNo i, double *Total, double *PredErr)
/*   -----------  */
{
    ContValue	Val, ModelVal, OldPred, NewPred;
    double	Wt;
    DataRec	C;

    C = Case[i];
    Val = Class(C);
    Wt = CWeight(C);
    Total[d] += Wt;

    CPredVal[i] = ModelVal = RawLinModel(Model, C);
    if ( ModelVal < Floor ) ModelVal = Floor;
    else
    if ( ModelVal > Ceiling ) ModelVal = Ceiling;

    if ( d )
    {
	OldPred = PredSum(C) / PredCount(C);
	NewPred = (PredSum(C) + ModelVal) / (PredCount(C) + 1);
	PredErr[d] += Wt * (fabs(Val - OldPred) - fabs(Val - NewPred));
    }
    else
    {
	PredErr[0] += Wt * fabs(Val - ModelVal);
    }
}



/*************************************************************************/
/*								  	 */
/*	Change Fail0, Fail1, and FailMany.				 */
/*									 */
/*	If Bestd has not been set, initialise the lists; otherwise	 */
/*	record the changes for deleting condition Bestd and reduce	 */
/*	LocalNFail for cases that do not satisfy condition Bestd	 */
/*								  	 */
/*************************************************************************/


void ProcessLists()
/*   ------------  */
{
    CaseNo	i, iNext, *Prev;
    int		d;

    if ( ! Bestd )
    {
	/*  Initialise the lists  */

	Fail0 = Fail1 = FailMany = -1;

	ForEach(d, 0, NCond)
	{
	    Total[d] = PredErr[d] = 0;
	}

	ForEach(i, 0, MaxCase)
	{
	    if ( ! LocalNFail[i] )
	    {
		UpdateCount(0, i, Total, PredErr);
		AddToList(&Fail0, i);
	    }
	    else
	    if ( LocalNFail[i] == 1 )
	    {
		d = SingleFail(i);
		UpdateCount(d, i, Total, PredErr);
		AddToList(&Fail1, i);
	    }
	    else
	    {
		AddToList(&FailMany, i);
	    }
	}
    }
    else
    {
	/*  Promote cases from Fail1 to Fail0  */

	Prev = &Fail1;

	for ( i = Fail1 ; i >= 0 ; )
	{
	    iNext = Succ[i];
	    if ( CondFailedBy[Bestd][i] )
	    {
		LocalNFail[i] = 0;
		UpdateCount(0, i, Total, PredErr);

		DeleteFromList(Prev, i);
		AddToList(&Fail0, i);
	    }
	    else
	    {
		Prev = &Succ[i];
	    }
	    i = iNext;
	}

	/*  Check cases in FailMany  */

	Prev = &FailMany;

	for ( i = FailMany ; i >= 0 ; )
	{
	    iNext = Succ[i];
	    if ( CondFailedBy[Bestd][i] && --LocalNFail[i] == 1 )
	    {
		d = SingleFail(i);
		UpdateCount(d, i, Total, PredErr);

		DeleteFromList(Prev, i);
		AddToList(&Fail1, i);
	    }
	    else
	    {
		Prev = &Succ[i];
	    }
	    i = iNext;
	}
    }
}



/*************************************************************************/
/*								  	 */
/*	Add case to list whose first case is *List			 */
/*								  	 */
/*************************************************************************/


void AddToList(CaseNo *List, CaseNo N)
/*   ---------  */
{
    Succ[N] = *List;
    *List   = N;
}



/*************************************************************************/
/*								  	 */
/*	Delete case from list where previous case is *Before		 */
/*								  	 */
/*************************************************************************/


void DeleteFromList(CaseNo *Before, CaseNo N)
/*   --------------  */
{
    *Before = Succ[N];
}



/*************************************************************************/
/*								  	 */
/*	Find single condition failed by a case				 */
/*								  	 */
/*************************************************************************/


int SingleFail(CaseNo i)
/*  ----------  */
{
    int		d;

    ForEach(d, 1, NCond)
    {
	if ( ! Deleted[d] && CondFailedBy[d][i] ) return d;
    }

    return 0;
}



/*************************************************************************/
/*									 */
/*	Make sure rule is approximately unbiased			 */
/*									 */
/*************************************************************************/


void RemoveBias(CRule R, int Coeffs)
/*   ----------  */
{
    double	Wt, TotErr=0, TotWt=0, TotAbsErr=-1, Bias=0, LastBias, New;
    CaseNo	i;

    /*  Computer initial bias and total weight  */

    for ( i = Fail0 ; i >= 0 ; )
    {
	Wt = CWeight(Case[i]);
	TotWt += Wt;

	New = ( CPredVal[i] < R->LoLim ? R->LoLim :
		CPredVal[i] > R->HiLim ? R->HiLim : CPredVal[i] );

	TotErr += Wt * (New - Class(Case[i]));

	i = Succ[i];
    }

    Bias = TotErr / TotWt;

    /*  Iteratively remove bias.  This cannot be done in a single step
	because range truncation can affect the mean residual  */

    while ( fabs((LastBias = Bias)) >= 0.5 * AttUnit[0] )
    {
	R->Rhs[0] -= Bias;

	TotErr = TotAbsErr = 0;

	for ( i = Fail0 ; i >= 0 ; )
	{
	    Wt = CWeight(Case[i]);

	    /*  Remove previous bias from raw value  */

	    CPredVal[i] -= Bias;

	    /*  Compute new range-limited value  */

	    New = ( CPredVal[i] < R->LoLim ? R->LoLim :
		    CPredVal[i] > R->HiLim ? R->HiLim : CPredVal[i] );

	    TotErr    += Wt * (New - Class(Case[i]));
	    TotAbsErr += Wt * fabs(New - Class(Case[i]));

	    i = Succ[i];
	}

	Bias = TotErr / TotWt;

	Verbosity(1, printf("bias %.5f  (%.2f / %.2f)\n", Bias, TotErr, TotWt))

	if ( fabs(Bias) >= fabs(LastBias) )
	{
	    break;
	}
    }

    /*  If any changes, reset the intercept precision and estimated error  */

    if ( TotAbsErr >= 0 )
    {
	R->Rhs[0] = rint(R->Rhs[0] / AttUnit[0]) * AttUnit[0];
	R->EstErr = EstimateErr(TotAbsErr / TotWt, R->Cover, Coeffs);
    }
}



/*************************************************************************/
/*									 */
/*	Sort rules by mean value					 */
/*									 */
/*************************************************************************/


void OrderRules(void)
/*   ----------  */
{
    RuleNo	r, nr, Next;
    CRule	Hold;

    ForEach(r, 1, NRules)
    {
	Next = r;
	ForEach(nr, r+1, NRules)
	{
	    if ( Rule[nr]->Mean < Rule[Next]->Mean )
	    {
		Next = nr;
	    }
	}

	Rule[Next]->RNo = r;
	if ( Next != r )
	{
	    Hold       = Rule[r];
	    Rule[r]    = Rule[Next];
	    Rule[Next] = Hold;
	}
    }
}



/*************************************************************************/
/*								  	 */
/*	Free all data allocated for forming rules			 */
/*								  	 */
/*************************************************************************/


void FreeFormRuleData(void)
/*   ----------------  */
{
    if ( ! CondFailedBy ) return;

    FreeVector((void **) CondFailedBy, 0, MaxDepth+1);	CondFailedBy = Nil;
    Free(Stack);					Stack = Nil;
    Free(Deleted);					Deleted = Nil;
    Free(Total);					Total = Nil;
    Free(PredErr);					PredErr = Nil;
    Free(NFail);					NFail = Nil;
    Free(LocalNFail);					LocalNFail = Nil;
    Free(Succ);						Succ = Nil;
    Free(CPredVal);					CPredVal = Nil;
}
