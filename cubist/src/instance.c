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

#include "defns.h"
#include "extern.h"

#include "redefine.h"
#include "transform.h"

#define DPREC 16 /* distance precision */

#define AdjustedValue(i, b)                                                    \
  (Cttee ? (Class(Instance[i]) + b - RSPredVal[i]) : Class(Instance[i]))

#define CVDiff(c, cv, a) (fabs(CVal(c, a) - (cv)) / (5 * AttSD[a]))

#define Select(t)                                                              \
  (UseAll ? (t) : (MaxInstance + 1) * ((2 * (t) + 1) / (2.0 * Try)))

int MinN; /* minimum close neighbors */

int Try;                  /* sample size for estimates */
Boolean UseAll,           /* true if no sampling */
    SetNN,                /* true if NN set automatically */
        *Tested = Nil;    /* for BuildIndex */
CaseCount *ValFreq = Nil; /* ditto */

AttValue *KDBlock; /* copy of instances in KDTree order to
                      improve caching  */

/*************************************************************************/
/*                                                                       */
/* Prepare for instance-based prediction     */
/*                                                                       */
/* The modified K-D tree algorithm adds to each instance the  */
/* distances to two "reference" points.  The first is an artifical  */
/* point intended to play the role of an origin: its value for an  */
/* attribute should be lower than most of the instances' values.  */
/* The second reference point is the instance that is furthest  */
/* from the first reference point.      */
/*                                                                       */
/*************************************************************************/

void InitialiseInstances(RRuleSet *Cttee)
/*   -------------------  */
{
  CaseNo i, FarInstance;
  Attribute Att;
  double Dist;

  /*  Use the data items as instances.  The vector Instance[] must
      be allocated separately since the indexing re-orders the items  */

  Instance = Alloc(MaxCase + 1, DataRec);
  MaxInstance = MaxCase;
  ForEach(i, 0, MaxCase) { Instance[i] = Case[i]; }

  Tested = AllocZero(MaxAtt + 1, unsigned char);
  ValFreq = Alloc(MaxDiscrVal + 1, CaseCount);

  GNNEnv.AttMinD = Alloc(MaxAtt + 1, float);

  /*  Construct the first reference point  */

  Ref[0] = Alloc(MaxAtt + 1, AttValue);
  ForEach(Att, 1, MaxAtt) {
    if (Continuous(Att)) {
      CVal(Ref[0], Att) = AttMean[Att] - 2.5 * AttSD[Att];
    } else {
      DVal(Ref[0], Att) = 2;
    }
  }

  /*  Compute distances and find an instance as far as possible from
      the first reference point  */

  FarInstance = 0;

  ForEach(i, 0, MaxInstance) {
    DRef1(Instance[i]) = Dist = Distance(Instance[i], Ref[0], 1E38);

    if (Dist > DRef1(Instance[FarInstance]))
      FarInstance = i;
  }

  Ref[1] = Alloc(MaxAtt + 1, AttValue);
  memcpy(Ref[1], Instance[FarInstance], (MaxAtt + 1) * sizeof(AttValue));

  /*  Now compute distances to the second reference point  */

  ForEach(i, 0, MaxInstance) {
    DRef2(Instance[i]) = Dist = Distance(Instance[i], Ref[1], 1E38);
  }

  NotifyStage(INDEXINSTANCES);
  Progress(-1.0);
  KDTree = BuildIndex(0, MaxCase);

  Free(Tested);
  Tested = Nil;
  Free(ValFreq);
  ValFreq = Nil;

  /*  Tabulate values predicted by ruleset.  Cannot use
      FindPredictedValues() because that would use instances!  */

  RSPredVal = Alloc(MaxCase + 1, float);

  ForEach(i, 0, MaxCase) { RSPredVal[i] = PredictValue(Cttee, Instance[i]); }

  /*  Set parameters for nearest neighbors if not read from model file  */

  Try = Min(MaxInstance + 1, 1000);
  UseAll = (Try == MaxInstance + 1);

  if (MAXD < 0) {
    SetParameters(Cttee);
  } else {
    SetNN = false;
  }

  MinN = (NN + 1) / 2;
  GNNEnv.WorstBest = GNNEnv.BestD + NN - 1;
}

/*************************************************************************/
/*                                                                       */
/* Set "close" distance MAXD to average distance.    */
/* If required, find the best NN value between 1 and NNMAX   */
/*                                                                       */
/*************************************************************************/

void SetParameters(RRuleSet *Cttee)
/*   -------------  */
{
  double TotErr[NNMAX + 1], Sum = 0;
  float Estimate, RealClass;
  CaseNo i, j;
  int t, BestNN = 1;

  /*  Set MAXD to the average distance between instances  */

  GNNEnv.WorstBest = GNNEnv.BestD; /* use single nearest neighbor */

  ForEach(t, 0, Try - 1) {
    i = Select(t);
    while ((j = KRandom() * (MaxInstance + 1)) == i)
      ;

    Sum += Distance(Instance[j], Instance[i], 1E10);
  }
  MAXD = rint(DPREC * Sum / Try) / DPREC;

  /*  Set NN if required  */

  if (NN) {
    SetNN = false;
  } else {
    SetNN = true;

    NotifyStage(SETNEIGHBORS);
    Progress(-Try);

    /*  Estimate error with different values of NN  */

    ForEach(NN, 1, NNMAX) { TotErr[NN] = 0; }
    GNNEnv.WorstBest = GNNEnv.BestD + NNMAX - 1;

    ForEach(t, 0, Try - 1) {
      i = Select(t);
      RealClass = Class(Instance[i]);

      FindNearestNeighbors(Instance[i]);

      ForEach(NN, 1, NNMAX) {
        MinN = (NN + 1) / 2;
        Estimate = AverageNeighbors(Cttee, Instance[i]);
        TotErr[NN] += fabs(RealClass - Estimate);
      }

      Progress(1.0);
    }

    /*  Select the best number of neighbors  */

    ForEach(NN, 2, NNMAX) {
      if (TotErr[NN] < TotErr[BestNN]) {
        BestNN = NN;
      }
    }

    ForEach(NN, 1, BestNN - 1) {
      if (TotErr[NN] < 1.01 * TotErr[BestNN]) {
        BestNN = NN;
        break;
      }
    }

    NN = BestNN;
    fprintf(Of, T_SettingNNeighbors, NN);
  }
}

/*************************************************************************/
/*                                                                       */
/* If allowed to choose, decide whether to use instances based  */
/* on estimated errors of rule-based and composite models   */
/*                                                                       */
/*************************************************************************/

void CheckForms(RRuleSet *Cttee)
/*   ----------  */
{
  CaseNo i;
  int t;
  double RSErr = 0, IErr = 0, RSIErr = 0, AvRules = 0;
  ContValue RealClass;

  NotifyStage(ASSESSCOMPOSITE);
  Progress(-Try);

  ForEach(t, 0, Try - 1) {
    i = Select(t);

    RealClass = Class(Case[i]);

    FindNearestNeighbors(Case[i]);
    IErr += fabs(RealClass - AverageNeighbors(Nil, Case[i]));

    RSErr += fabs(RealClass - PredictValue(Cttee, Case[i]));

    RSIErr += fabs(RealClass - AverageNeighbors(Cttee, Case[i]));
    Progress(1.0);
  }

  /*  Find average number of rules in cttee  */

  ForEach(i, 0, MEMBERS - 1) { AvRules += Cttee[i]->SNRules; }
  AvRules /= MEMBERS;

  if (!SetNN)
    fprintf(Of, "\n\n");

  Verbosity(1, fprintf(Of, "\n\n    %s |error| on training data:\n",
                       (UseAll ? "Average" : "Sampled"));
            fprintf(Of, "\tinstances:\t\t%.2f\n", IErr / Try);
            fprintf(Of, "\trules:\t\t\t%.2f\n", RSErr / Try);
            fprintf(Of, "\trules + instances:\t%.2f\n", RSIErr / Try))

      if (EstimateErr(RSErr, MaxCase + 1, 2 * AvRules) <
          EstimateErr(RSIErr, MaxCase + 1, AvRules)) {
    USEINSTANCES = false;
    fprintf(Of, T_SuggestRules);
    FreeInstances();
  }
  else {
    fprintf(Of, T_SuggestComposite);
  }
}

/*************************************************************************/
/*                                                                       */
/* Make a copy of instances in KDTree order to improve caching  */
/*                                                                       */
/*************************************************************************/

void CopyInstances(void)
/*   -------------  */
{
  AttValue *KDBlockP;
  CaseNo i;

  KDBlockP = KDBlock = Alloc((MaxInstance + 1) * (MaxAtt + 3), AttValue);
  ForEach(i, 0, MaxInstance) {
    memcpy(KDBlockP, Instance[i], (MaxAtt + 3) * sizeof(AttValue));
    Instance[i] = KDBlockP;
    KDBlockP += MaxAtt + 3;
  }
}

/*************************************************************************/
/*                                                                       */
/* Use nearest neighbors to estimate target for Case.   */
/* If Cttee is not null, values of neighbors are adjusted by  */
/* rulesets before being combined.       */
/*                                                                       */
/*************************************************************************/

float NNEstimate(RRuleSet *Cttee, DataRec Case)
/*    ----------  */
{
  FindNearestNeighbors(Case);

  return AverageNeighbors(Cttee, Case);
}

/*************************************************************************/
/*                                                                       */
/* Determine the distance between two cases.    */
/* Stop if the distance becomes too great to be relevant.   */
/*                                                                       */
/* Cubist uses Manhattan distance between instances (i.e. sum  */
/* of the attribute differences).  These are defined as:   */
/* * discrete att: 0 (if same) or 2 / number of discrete values  */
/* * continuous att: difference / 5 SD     */
/*                                                                       */
/*************************************************************************/

float Distance(DataRec Case1, DataRec Case2, float Thresh)
/*    --------  */
{
  Attribute Att;
  double DTot, Diff;

  for (Att = 1, DTot = 0; DTot < Thresh && Att <= MaxAtt; Att++) {
    if (Skip(Att) || Att == ClassAtt)
      continue;

    if (NotApplic(Case2, Att) != NotApplic(Case1, Att)) {
      DTot += 1.0;
    } else if (Continuous(Att)) {
      Diff = CVDiff(Case2, CVal(Case1, Att), Att);
      DTot += Min(1.0, Diff);
    } else if (Ordered(Att)) {
      DTot += abs(DVal(Case2, Att) - DVal(Case1, Att)) / (MaxAttVal[Att] - 1);
    } else if (DVal(Case2, Att) != DVal(Case1, Att)) {
      DTot += 2.0 / (MaxAttVal[Att] - 1);
    }
  }

  return DTot;
}

/*************************************************************************/
/*                                                                       */
/* Check whether a saved instance should be one of the neighbors.  */
/* Distances are rounded to precision 1/DPREC    */
/*                                                                       */
/*************************************************************************/

void CheckDistance(DataRec Case, CaseNo Saved)
/*   -------------  */
{
  int d, dd;
  float Dist;

  if (Instance[Saved] == Case)
    return;

  Dist = rint(DPREC * Distance(Case, Instance[Saved],
                               *GNNEnv.WorstBest + 0.55 / DPREC)) /
         DPREC;

  if (Dist <= *GNNEnv.WorstBest) {
    for (d = 0; d < MAXN && GNNEnv.BestD[d] < Dist; d++)
      ;

    if (d < MAXN) {
      for (dd = MAXN - 1; dd > d; dd--) {
        GNNEnv.BestD[dd] = GNNEnv.BestD[dd - 1];
        GNNEnv.BestI[dd] = GNNEnv.BestI[dd - 1];
      }

      GNNEnv.BestD[d] = Dist;
      GNNEnv.BestI[d] = Saved;
    }
  }
}

/*************************************************************************/
/*                                                                       */
/* Find the NN nearest saved instances to a given case.   */
/* KD-trees are used to locate neighbors quickly.    */
/*                                                                       */
/*************************************************************************/

void FindNearestNeighbors(DataRec Case)
/*   --------------------  */
{
  int d;
  Attribute Att;

  /*  Clear best distances and attribute minimum distances  */

  ForEach(d, 0, MAXN - 1) {
    GNNEnv.BestD[d] = MAXD;
    GNNEnv.BestI[d] = -1;
  }

  ForEach(Att, 1, MaxAtt) { GNNEnv.AttMinD[Att] = 0; }

  DRef1(Case) = Distance(Case, Ref[0], 1E38);
  DRef2(Case) = Distance(Case, Ref[1], 1E38);

  ScanIndex(Case, KDTree, 0.0);
}

/*************************************************************************/
/*                                                                       */
/* Find weighted average value of selected neighbors.   */
/* [Weight = 1 / (Manhattan distance + 0.5).]    */
/* Have to be careful with ties.      */
/*                                                                       */
/*************************************************************************/

float AverageNeighbors(RRuleSet *Cttee, DataRec Case)
/*    ----------------  */
{
  int d = 0, Count = 0, Same, Last;
  double Est, BaseEst, Wt, SameSum, SameWt, TotSum = 0, TotWt = 0;

  BaseEst = (Cttee ? PredictValue(Cttee, Case) : GlobalMean);

  /*  Check the number of neighbors actually found  */

  for (Last = MAXN - 1; Last >= 0 && GNNEnv.BestI[Last] < 0; Last--)
    ;

  if (Last + 1 < MinN) {
    return BaseEst;
  }

  /*  Extract groups of neighbors with the same values of BestD  */

  while (d <= Last && Count < NN && Count < MaxInstance) {
    SameSum = SameWt = Same = 0;
    Wt = 1 / (GNNEnv.BestD[d] + 0.5);
    do {
      Est = AdjustedValue(GNNEnv.BestI[d], BaseEst);
      if (Est > Ceiling)
        Est = Ceiling;
      else if (Est < Floor)
        Est = Floor;

      SameSum += Wt * Est;
      SameWt += Wt;

      Same++;
      d++;
    } while (d <= Last && GNNEnv.BestD[d] == GNNEnv.BestD[d - 1]);

    if (Count + Same > NN) {
      Wt = (NN - Count) / (float)Same;
      TotSum += Wt * SameSum;
      TotWt += Wt * SameWt;
      Count = NN;
    } else {
      TotSum += SameSum;
      TotWt += SameWt;
      Count += Same;
    }
  }

  Est = TotSum / TotWt;
  return (Est < Floor ? Floor : Est > Ceiling ? Ceiling : Est);
}

/*************************************************************************/
/*                                                                       */
/* The following routines are concerned with indexing the   */
/* instances in a KD-tree, and using the tree to locate nearest  */
/* neighbors without having to examine each saved instance.  */
/* Note that BuildIndex() can create branches that have no cases  */
/* associated with them -- this is ok since it speeds up   */
/* ScanIndex() by increasing MinD.      */
/*                                                                       */
/*************************************************************************/

Index BuildIndex(CaseNo Fp, CaseNo Lp)
/*    ----------  */
{
  Index Node;
  DiscrValue v, vv;
  CaseNo i, Xp, Kp;
  CaseCount Cases;
  double Mean, BestMean, ExpDist, BestExpDist = 0, ProbNA;
  float Dist, MinDRef[2], MaxDRef[2];
  Attribute Att, BestAtt = 0;

  if (Lp < Fp)
    return Nil;

  Node = AllocZero(1, IndexRec);

  if (Lp > Fp) {
    MinDRef[0] = MaxDRef[0] = DRef1(Instance[Fp]);
    MinDRef[1] = MaxDRef[1] = DRef2(Instance[Fp]);

    ForEach(i, Fp + 1, Lp) {
      if ((Dist = DRef1(Instance[i])) < MinDRef[0]) {
        MinDRef[0] = Dist;
      } else if (Dist > MaxDRef[0]) {
        MaxDRef[0] = Dist;
      }

      if ((Dist = DRef2(Instance[i])) < MinDRef[1]) {
        MinDRef[1] = Dist;
      } else if (Dist > MaxDRef[1]) {
        MaxDRef[1] = Dist;
      }
    }

    Node->MinDRef[0] = MinDRef[0];
    Node->MaxDRef[0] = MaxDRef[0];
    Node->MinDRef[1] = MinDRef[1];
    Node->MaxDRef[1] = MaxDRef[1];

    /*  Find the attribute with the greatest expected difference.
        Distances to the reference points are candidates  */

    ForEach(Att, 1, MaxAtt) {
      if (Skip(Att) || Att == ClassAtt || (Tested[Att] && Discrete(Att))) {
        continue;
      }

      /*  Separate all N/A values (real attributes only)  */

      Xp = Fp;
      ForEach(i, Fp, Lp) {
        if (NotApplic(Instance[i], Att)) {
          SwapInstance(i, Xp++);
        }
      }

      ProbNA = (Xp - Fp) / (Lp - Fp + 1.0);
      if (!(Cases = Lp - Xp + 1))
        continue;

      ExpDist = Mean = 0;

      if (Continuous(Att)) {
        /*  Expected distance is average difference from mean  */

        ForEach(i, Xp, Lp) { Mean += CVal(Instance[i], Att); }
        Mean /= Cases;

        ForEach(i, Xp, Lp) { ExpDist += CVDiff(Instance[i], Mean, Att); }
        ExpDist /= Cases;
      } else {
        /*  Expected distance is computed from pairwise differences
            of values  */

        ForEach(v, 2, MaxAttVal[Att]) { ValFreq[v] = 0; }

        ForEach(i, Xp, Lp) { ValFreq[DVal(Instance[i], Att)]++; }

        if (Ordered(Att)) {
          ForEach(v, 2, MaxAttVal[Att]) {
            ForEach(vv, 2, MaxAttVal[Att]) {
              ExpDist += ValFreq[v] * ValFreq[vv] * abs(vv - v);
            }
          }
        } else {
          ForEach(v, 2, MaxAttVal[Att]) {
            ExpDist += ValFreq[v] * (Cases - ValFreq[v]) * 2.0;
          }
        }

        ExpDist /= (MaxAttVal[Att] - 1) * Cases * Cases;
      }

      /*  Final expected distance =
              (prob one or other N/A) * 1 +
              (prob both known) * (expected distance if known)  */

      ExpDist =
          2 * ProbNA * (1 - ProbNA) + (1 - ProbNA) * (1 - ProbNA) * ExpDist;

      if (ExpDist > BestExpDist) {
        BestExpDist = ExpDist;
        BestAtt = Att;
        BestMean = Mean;
      }
    }
  }

  /*  Check whether leaf or sub-index  */

  if (!BestAtt) {
    Node->Tested = 0;
    Node->IFp = Fp;
    Node->ILp = Lp;
  } else if (Discrete(BestAtt)) {
    Node->Tested = BestAtt;
    Node->SubIndex = Alloc(MaxAttVal[BestAtt] + 1, Index);

    Tested[BestAtt] = true;

    /*  Sort instances by attribute value  */

    Kp = Fp;
    ForEach(v, 1, MaxAttVal[BestAtt]) {
      ForEach(Xp, Kp, Lp) {
        if (DVal(Instance[Xp], BestAtt) == v) {
          SwapInstance(Xp, Kp++);
        }
      }

      Node->SubIndex[v] = BuildIndex(Fp, Kp - 1);
      Fp = Kp;
    }

    Tested[BestAtt] = false;
  } else {
    Node->Tested = BestAtt;
    Node->Cut = BestMean;

    /*  There are three branches for continuous attributes:
        N/A / value <= mean / value > mean  */

    Xp = Fp;
    ForEach(i, Fp, Lp) {
      if (NotApplic(Instance[i], BestAtt)) {
        SwapInstance(i, Xp++);
      }
    }

    Kp = Xp;
    ForEach(i, Xp, Lp) {
      if (CVal(Instance[i], BestAtt) <= BestMean) {
        SwapInstance(i, Kp++);
      }
    }

    /*  Safety check:  return leaf if not a sensible split  */

    if (Xp == Lp + 1 || (Xp == Fp && Kp == Lp + 1) || Kp == Fp) {
      Node->Tested = 0;
      Node->IFp = Fp;
      Node->ILp = Lp;
    } else {
      Node->SubIndex = Alloc(4, Index);
      Node->SubIndex[1] = BuildIndex(Fp, Xp - 1);
      Node->SubIndex[2] = BuildIndex(Xp, Kp - 1);
      Node->SubIndex[3] = BuildIndex(Kp, Lp);
    }
  }

  return Node;
}

void SwapInstance(CaseNo A, CaseNo B)
/*   ------------  */
{
  DataRec Hold;

  Hold = Instance[A];
  Instance[A] = Instance[B];
  Instance[B] = Hold;
}

void ScanIndex(DataRec Case, Index Node, float MinD)
/*   ---------  */
{
  CaseNo Xp;
  DiscrValue Forks, First, v;
  float NewMinD, SaveAttMinD;
  Attribute Att;

  if (Node == Nil)
    return;

  if (!(Att = Node->Tested)) {
    ForEach(Xp, Node->IFp, Node->ILp) { CheckDistance(Case, Xp); }
  } else if (Max(Node->MinDRef[0] - DRef1(Case),
                 DRef1(Case) - Node->MaxDRef[0]) <=
                 *GNNEnv.WorstBest + 0.5 / DPREC &&
             Max(Node->MinDRef[1] - DRef2(Case),
                 DRef2(Case) - Node->MaxDRef[1]) <=
                 *GNNEnv.WorstBest + 0.5 / DPREC) {
    if (Discrete(Att)) {
      First = DVal(Case, Att);
      Forks = MaxAttVal[Att];
    } else {
      First = (NotApplic(Case, Att) ? 1 : CVal(Case, Att) <= Node->Cut ? 2 : 3);
      Forks = 3;
    }

    /*  Try best sub-index first, then other sub-indices so long
        as can improve on current best neighbors  */

    if (First <= Forks) {
      ScanIndex(Case, Node->SubIndex[First], MinD);
    }

    SaveAttMinD = GNNEnv.AttMinD[Att];

    ForEach(v, 1, Forks) {
      if (v == First || !Node->SubIndex[v])
        continue;

      GNNEnv.AttMinD[Att] =
          (v == 1 || First == 1
               ? 1.0
               : Continuous(Att)
                     ? CVDiff(Case, Node->Cut, Att)
                     : Ordered(Att) ? abs(v - First) / (MaxAttVal[Att] - 1)
                                    : 2.0 / (MaxAttVal[Att] - 1));
      NewMinD = MinD + GNNEnv.AttMinD[Att] - SaveAttMinD;

      if (NewMinD <= *GNNEnv.WorstBest + 0.5 / DPREC) {
        ScanIndex(Case, Node->SubIndex[v], NewMinD);
      }
    }

    GNNEnv.AttMinD[Att] = SaveAttMinD;
  }
}

void FreeIndex(Index Node)
/*   ---------  */
{
  DiscrValue v, Forks;
  Attribute Att;

  if (Node == Nil)
    return;

  if ((Att = Node->Tested)) {
    Forks = (Discrete(Att) ? MaxAttVal[Att] : 3);
    ForEach(v, 1, Forks) { FreeIndex(Node->SubIndex[v]); }
    Free(Node->SubIndex);
  }

  Free(Node);
}

void FreeInstances(void)
/*   -------------  */
{
  if (Instance) {
    Free(Instance);
    Instance = Nil;
    Free(KDBlock);
    KDBlock = Nil;
  }

  FreeUnlessNil(GNNEnv.AttMinD);
  GNNEnv.AttMinD = Nil;
  FreeUnlessNil(RSPredVal);
  RSPredVal = Nil;

  if (KDTree) {
    FreeUnlessNil(Ref[0]);
    Ref[0] = Nil;
    FreeUnlessNil(Ref[1]);
    Ref[1] = Nil;
    FreeIndex(KDTree);
    KDTree = Nil;
  }
}
