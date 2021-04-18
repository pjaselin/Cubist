/*************************************************************************/
/*                                                                       */
/*  Copyright 2010 Rulequest Research Pty Ltd.                           */
/*                                                                       */
/*  This file is part of Cubist GPL Edition, a single-threaded version   */
/*  of Cubist release 2.07.                                              */
/*                                                                       */
/*  Cubist GPL Edition is free software: you can redistribute it and/or  */
/*  modify it under the terms of the GNU General Public License as       */
/*  published by the Free Software Foundation, either version 3 of the   */
/*  License, or (at your option) any later version.                      */
/*                                                                       */
/*  Cubist GPL Edition is distributed in the hope that it will be        */
/*  useful, but WITHOUT ANY WARRANTY; without even the implied warranty  */
/*  of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the     */
/*  GNU General Public License for more details.                         */
/*                                                                       */
/*  You should have received a copy of the GNU General Public License    */
/*  (gpl.txt) along with Cubist GPL Edition.  If not, see                */
/*                                                                       */
/*      <http://www.gnu.org/licenses/>.                                  */
/*                                                                       */
/*************************************************************************/

/*************************************************************************/
/*           */
/*    Central tree-forming algorithm      */
/*    ------------------------------      */
/*           */
/*************************************************************************/

#include "defns.h"
#include "extern.h"

#include <stdint.h>

#include "redefine.h"
#include "transform.h"

/*************************************************************************/
/*           */
/* Allocate space for tree tables       */
/*           */
/*************************************************************************/

void InitialiseEnvData(void)
/*   -----------------  */
{
  DiscrValue v;
  Attribute Att;

  SRec = Alloc(MaxCase + 1, SortRec);

  /*  Set up environment  */

  GEnv.LocalModel = AllocZero(MaxAtt + 1, double);

  GEnv.ValFreq = Alloc(MaxDiscrVal + 1, double);
  GEnv.ValSum = Alloc(MaxDiscrVal + 1, double);
  GEnv.ValSumSq = Alloc(MaxDiscrVal + 1, double);

  GEnv.Gain = AllocZero(MaxAtt + 1, float);
  GEnv.Bar = AllocZero(MaxAtt + 1, ContValue);

  /*  Data for subsets  */

  GEnv.Left = Alloc(MaxDiscrVal + 1, Boolean);
  GEnv.Subset = AllocZero(MaxAtt + 1, Set *);

  ForEach(Att, 1, MaxAtt) {
    if (Discrete(Att)) {
      GEnv.Subset[Att] = AllocZero(4, Set);
      ForEach(v, 1, 3) {
        GEnv.Subset[Att][v] = Alloc((MaxAttVal[Att] >> 3) + 1, unsigned char);
      }
    }
  }

  /*  Stuff for forming linear models by matrix inversion  */

  GEnv.xTx = Alloc(MaxAtt + 1, double *);
  GEnv.A = Alloc(MaxAtt + 1, double *);
  ForEach(Att, 0, MaxAtt) {
    GEnv.xTx[Att] = Alloc(MaxAtt + 1, double);
    GEnv.A[Att] = Alloc(MaxAtt + 1, double);
  }
  GEnv.xTy = Alloc(MaxAtt + 1, double);
  GEnv.B = Alloc(MaxAtt + 1, double);

  GEnv.Resid = Alloc(MaxCase + 1, double);
  GEnv.PResid = Alloc(MaxCase + 1, double);

  GEnv.Mean = Alloc(MaxAtt + 1, double);
  GEnv.Var = Alloc(MaxAtt + 1, double);
  GEnv.AvDev = Alloc(MaxAtt + 1, double);

  GEnv.ZeroCoeff = AllocZero(MaxAtt + 1, Boolean);

  GEnv.BestModel = Alloc(MaxAtt + 1, double);
  GEnv.SaveZero = Alloc(MaxAtt + 1, Boolean);

  GEnv.Filtered = Alloc(MaxCase + 1, DataRec);

  GEnv.DoNotUse = Alloc(MaxAtt + 1, Boolean);

  GEnv.ModelAtt = Alloc(MaxAtt + 1, Attribute);
}

void FreeEnvData(void)
/*   ------------  */
{
  Attribute Att;

  if (!GEnv.LocalModel)
    return;

  FreeUnlessNil(GEnv.LocalModel);

  FreeUnlessNil(GEnv.ValFreq);
  FreeUnlessNil(GEnv.ValSum);
  FreeUnlessNil(GEnv.ValSumSq);

  FreeUnlessNil(GEnv.Gain);
  FreeUnlessNil(GEnv.Bar);

  FreeUnlessNil(GEnv.Left);
  ForEach(Att, 1, MaxAtt) {
    if (Discrete(Att)) {
      FreeVector((void **)GEnv.Subset[Att], 1, 3);
    }
  }
  FreeUnlessNil(GEnv.Subset);

  FreeVector((void **)GEnv.xTx, 0, MaxAtt);
  FreeVector((void **)GEnv.A, 0, MaxAtt);
  FreeUnlessNil(GEnv.xTy);
  FreeUnlessNil(GEnv.B);

  FreeUnlessNil(GEnv.Resid);
  FreeUnlessNil(GEnv.PResid);

  FreeUnlessNil(GEnv.Mean);
  FreeUnlessNil(GEnv.Var);
  FreeUnlessNil(GEnv.AvDev);

  FreeUnlessNil(GEnv.ZeroCoeff);

  FreeUnlessNil(GEnv.BestModel);
  FreeUnlessNil(GEnv.SaveZero);

  FreeUnlessNil(GEnv.Filtered);

  FreeUnlessNil(GEnv.DoNotUse);

  FreeUnlessNil(GEnv.ModelAtt);

  FreeUnlessNil(SRec);
  SRec = Nil;
}

/*************************************************************************/
/*           */
/* Set global preferences for continuous attributes and find  */
/* statistics for global target values.     */
/*           */
/* Attribute preference is determined by counting the number of  */
/* times the sign of the deviations of the attribute and the  */
/* target value agree.  Very low or very high values are better.  */
/*           */
/*************************************************************************/

void FindGlobalProperties(void)
/*   --------------------  */
{
  int *N, *Same;
  CaseNo i;
  Attribute Att;
  Boolean AboveAv;
  ContValue Val;
  double Sum = 0, SumSq = 0, Wt, MinCoeff;

  Verbosity(1, fprintf(Of, "\nPreference values:\n"))

      N = AllocZero(MaxAtt + 1, int);
  Same = AllocZero(MaxAtt + 1, int);

  ForEach(i, 0, MaxCase) {
    Wt = CWeight(Case[i]);

    Sum += Wt * (Val = Class(Case[i]));
    SumSq += Wt * Val * Val;

    AboveAv = (Val > AttMean[ClassAtt]);

    ForEach(Att, 1, MaxAtt) {
      /*  Exclude everything except continuous predictor attributes
          and also discard non-applicable or unknown values  */

      if (!Skip(Att) && !Discrete(Att) && Att != ClassAtt &&
          !NotApplic(Case[i], Att) &&
          (Val = CVal(Case[i], Att)) != AttMean[Att]) {
        N[Att]++;
        Same[Att] += ((Val > AttMean[Att]) == AboveAv);
      }
    }
  }

  GlobalMean = Sum / (MaxCase + 1);
  GlobalSD = SD(MaxCase + 1, Sum, SumSq);
  GlobalErr = AverageDev(GlobalMean, 0, MaxCase);

  AttUnit[0] = 1.0 / AttPrec[ClassAtt];

  ForEach(Att, 1, MaxAtt) {
    if (Skip(Att) || Discrete(Att) || Att == ClassAtt || !N[Att]) {
      AttPref[Att] = 0;
    } else {
      AttPref[Att] = (2 * Max(Same[Att], N[Att] - Same[Att]) - N[Att]) /
                     (double)(MaxCase + 1);

      Verbosity(1, fprintf(Of, "%6.3f  %s\n", AttPref[Att], AttName[Att]))

          /*  Set coefficient unit for attribute so that
              AttUnit[Att] * AttSD[Att] <= UNITFRAC * GlobalSD  */

          AttUnit[Att] = 1;
      MinCoeff = MinAttCoeff(Att);
      if (MinCoeff > 0) {
        for (; AttUnit[Att] > MinCoeff; AttUnit[Att] /= 10)
          ;
      }
    }
  }

  free(N);
  free(Same);
}

/*************************************************************************/
/*           */
/* Build a regression tree for the cases Fp through Lp    */
/*           */
/*************************************************************************/

void FormTree(CaseNo Fp, CaseNo Lp, int Level, Tree *Result, Tree Parent)
/*   --------  */
{
  CaseNo i;
  ContValue BestVal, Val, MaxResid;
  double Cases = 0, Wt, RawSum = 0, Sum = 0, SumSq = 0;
  Attribute Att, BestAtt;
  Tree Node, P;
  Boolean Root;

  Verbosity(1, fprintf(Of, "\n<%d> %d cases\n", Level, Lp - Fp + 1))

      /*  Find local model and residuals  */

      if (!(Root = (Lp - Fp >= MaxCase))) {
    ForEach(Att, 1, MaxAtt) { GEnv.DoNotUse[Att] = true; }

    for (P = Parent; P; P = Parent(P)) {
      GEnv.DoNotUse[P->Tested] = false;
    }

    AddDefAtts();

    Regress(Fp, Lp, GEnv.LocalModel);

    FindModelAtts(GEnv.LocalModel);
  }
  else {
    ForEach(Att, 0, MaxAtt) { GEnv.LocalModel[Att] = 0; }

    GEnv.NModelAtt = 0;
  }

  MaxResid = 0;

  ForEach(i, Fp, Lp) {
    Wt = CWeight(Case[i]);
    Val = Resid(Case[i]) =
        (Root ? Class(Case[i])
              : Class(Case[i]) - LinModel(GEnv.LocalModel, Case[i]));
    Cases += Wt;
    RawSum += Wt * Class(Case[i]);
    Sum += Wt * Val;
    SumSq += Wt * Val * Val;

    if ((Val = fabs(Val)) > MaxResid)
      MaxResid = Val;
  }

  /*  Establish root of this subtree  */

  *Result = Node = Leaf(Lp - Fp + 1, RawSum / Cases, SD(Cases, Sum, SumSq));

  if (Root) {
    Node->Model[0] = Node->Mean;
  } else {
    memcpy(Node->Model, GEnv.LocalModel, (MaxAtt + 1) * sizeof(double));
  }

  /*  If the maximum residual is smaller than the desired model
      precision, there is no need to go further  */

  if (MaxResid < 0.5 * AttUnit[0]) {
    Verbosity(1, fprintf(Of, "negligible residuals\n")) Progress(Cases);
    return;
  }

  /*  Find the attribute with maximum gain  */

  BestVal = -Epsilon;
  BestAtt = None;

  ForEach(Att, 1, MaxAtt) {
    GEnv.Gain[Att] = None;

    if (Skip(Att) || Att == ClassAtt)
      continue;

    if (Discrete(Att)) {
      if (Root || MaxAttVal[Att] > 3 || GEnv.DoNotUse[Att]) {
        EvalDiscreteAtt(Node, Att, Fp, Lp);
      }
    } else {
      EvalContinuousAtt(Node, Att, Fp, Lp);
    }

    if ((Val = GEnv.Gain[Att]) > -Epsilon) {
      if (Val > BestVal ||
          (Val > 0.999 * BestVal && AttPref[Att] > AttPref[BestAtt])) {
        BestAtt = Att;
        BestVal = Val;
      }
    }
  }

  /*  Decide whether to branch or not  */

  if (BestAtt == None) {
    Verbosity(1, fprintf(Of, "no sensible splits\n")) Progress(Cases);
  } else {
    Verbosity(
        1, fprintf(Of, "best attribute %s", AttName[BestAtt]);
        if (Continuous(BestAtt)) {
          fprintf(Of, " cut %.3f", GEnv.Bar[BestAtt]);
        } fprintf(Of, " gain %.3f\n", GEnv.Gain[BestAtt]);)

        /*  Build a node of the selected test  */

        if (Discrete(BestAtt)) {
      DiscreteTest(Node, BestAtt, GEnv.Subset[BestAtt]);
    }
    else {
      ContinTest(Node, BestAtt, GEnv.Bar[BestAtt]);
    }

    /*  Record parent of this node  */

    Parent(Node) = Parent;

    /*  Carry out the recursive divide-and-conquer  */

    Divide(Node, Fp, Lp, Level);
  }
}

void AddModels(CaseNo Fp, CaseNo Lp, Tree T, Tree Parent)
/*   ---------  */
{
  Attribute Att;
  CaseNo Bp, Ep;
  DiscrValue v;

  Progress(1.0);

  if (!T->Cases)
    return;

  if (T->NodeType) {
    Bp = Fp;
    ForEach(v, 1, T->Forks) {
      if (T->Branch[v]->Cases) {
        Ep = Bp + T->Branch[v]->Cases - 1;
        AddModels(Bp, Ep, T->Branch[v], T);
        Bp = Ep + 1;
      }
    }
  }

  /*  Find a new model for this node  */

  ForEach(Att, 1, MaxAtt) { GEnv.DoNotUse[Att] = true; }

  while (Parent) {
    if (Continuous((Att = Parent->Tested))) {
      GEnv.DoNotUse[Att] = false;
    }

    Parent = Parent(Parent);
  }

  AddSplitAtts(T);
  AddDefAtts();

  Regress(Fp, Lp, T->Model);
}

/*************************************************************************/
/*           */
/* Form the subtrees for the given node     */
/*           */
/*************************************************************************/

void Divide(Tree Node, CaseNo Fp, CaseNo Lp, int Level)
/*   ------  */
{
  CaseNo Ep;
  DiscrValue v;
#ifdef VerbOpt
  CaseNo XEp[4]; /*  Queue tasks in non-SMP order  */
  XEp[0] = Fp - 1;
#endif

  /* gets flagged by R CMD check, uncomment for debugging */
  /* assert(Node->Forks < 4); */

  /*  Recursive divide and conquer  */

  ForEach(v, 1, Node->Forks) {
    Ep = Group(v, Fp, Lp, Node);

#ifdef VerbOpt
    XEp[v] = Ep;
#endif
    if (Fp <= Ep) {
      FormTree(Fp, Ep, Level + 1, &Node->Branch[v], Node);
      Fp = Ep + 1;
    } else {
      Node->Branch[v] = Leaf(0, Node->Mean, Node->SD);
    }
  }
}

/*************************************************************************/
/*           */
/* Group together the items corresponding to branch V of a test   */
/* and return the index of the last such      */
/*           */
/* Note: if V equals zero, group the unknown values    */
/*           */
/*************************************************************************/

CaseNo Group(DiscrValue V, CaseNo Fp, CaseNo Lp, Tree TestNode)
/*     -----  */
{
  CaseNo i;
  Attribute Att;
  ContValue Thresh;
  Set SS;
  DataRec xab;

  Att = TestNode->Tested;

  /*  Group items on the value of attribute Att, and depending
      on the type of branch  */

  switch (TestNode->NodeType) {
  case BrDiscr:

    ForEach(i, Fp, Lp) {
      if (DVal(Case[i], Att) == V) {
        Swap(Fp, i);
        Fp++;
      }
    }
    break;

  case BrThresh:

    Thresh = TestNode->Cut;
    ForEach(i, Fp, Lp) {
      if (V == 1 ? NotApplic(Case[i], Att)
                 : (CVal(Case[i], Att) <= Thresh) == (V == 2)) {
        Swap(Fp, i);
        Fp++;
      }
    }
    break;

  case BrSubset:

    SS = TestNode->Subset[V];
    ForEach(i, Fp, Lp) {
      if (In(DVal(Case[i], Att), SS)) {
        Swap(Fp, i);
        Fp++;
      }
    }
    break;
  }

  return Fp - 1;
}

/*************************************************************************/
/*           */
/* Add the continuous attributes that are used in a branch of  */
/* the tree to those that can be used in a model    */
/*           */
/*************************************************************************/

void AddSplitAtts(Tree T)
/*   ------------  */
{
  DiscrValue v;

  if (T->NodeType) {
    if (Continuous(T->Tested)) {
      GEnv.DoNotUse[T->Tested] = false;
    }

    ForEach(v, 1, T->Forks) { AddSplitAtts(T->Branch[v]); }
  }
}

/*************************************************************************/
/*           */
/* If attribute A can be used in a model, then so can any   */
/* implicitly-defined attribute that uses A    */
/*           */
/*************************************************************************/

void AddDefAtts(void)
/*   ----------  */
{
  Attribute Att;
  Definition D;
  int e;

  ForEach(Att, 1, MaxAtt) {
    if (GEnv.DoNotUse[Att] && (D = AttDef[Att])) {
      for (e = 0;; e++) {
        if (DefOp(D[e]) == OP_ATT &&
            !GEnv.DoNotUse[(long)(intptr_t)DefSVal(D[e])]) {
          Verbosity(2, fprintf(Of, "adding %s from %s\n", AttName[Att],
                               AttName[(int)DefSVal(D[e])]))
              GEnv.DoNotUse[Att] = false;
          break;
        } else if (DefOp(D[e]) == OP_END) {
          break;
        }
      }
    }
  }
}

/*************************************************************************/
/*           */
/* Find attributes used in a model (speeds up LinModel)   */
/*           */
/*************************************************************************/

void FindModelAtts(double *Model)
/*   -------------  */
{
  Attribute Att;

  GEnv.NModelAtt = 0;
  ForEach(Att, 1, MaxAtt) {
    if (Model[Att]) {
      GEnv.ModelAtt[++GEnv.NModelAtt] = Att;
    }
  }
}
