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
/*                                                                       */
/* Routines for constructing rulesets and committees   */
/* -------------------------------------------------   */
/*                                                                       */
/*************************************************************************/

#include "defns.h"
#include "extern.h"
#include <time.h>

#include "redefine.h"
#include "transform.h"

/*************************************************************************/
/*                                                                       */
/*      Construct, save and evaluate a single model    */
/*                                                                       */
/*************************************************************************/

void SingleCttee(void)
/*   -----------  */
{
  FILE *F;

  ConstructCttee();

  /*  Evaluation  */

  fprintf(Of, T_EvalTrain, MaxCase + 1,
          (USEINSTANCES && MaxCase > 20000 ? ", sampled" : ""));

  NotifyStage(EVALTRAIN);
  Progress(-(MaxCase + 1.0));

  EvaluateCttee(Cttee, false);

  if ((F = GetFile((SAMPLE ? ".data" : ".test"), "r"))) {
    NotifyStage(READTEST);
    Progress(-1.0);

    fprintf(Of, "\n");

    if (USEINSTANCES) {
      Free(Case); /* leave actual descriptions */
    } else {
      FreeData(Case);
    }
    Case = Nil;

    GetData(F, false, false);

    fprintf(Of, T_EvalTest, MaxCase + 1);

    NotifyStage(EVALTEST);
    Progress(-(MaxCase + 1.0));

    EvaluateCttee(Cttee, true);
  } else if ((F = GetFile(".pred", "r"))) {
    fclose(F);
    remove(Fn); /* set by GetFile */
  }

  FreeCttee(Cttee);
  Cttee = Nil;
}

/*************************************************************************/
/*                                                                       */
/*      Main construction routines      */
/*                                                                       */
/*************************************************************************/

void ConstructCttee(void)
/*   --------------  */
{
  int m;
  Boolean SaveUSEINSTANCES;
  CaseNo i;
  double Cases, SumErr = 0, Err, FinalErr = 0;

  /*  Preserve original item order  */

  SaveCase = Alloc(MaxCase + 1, DataRec);
  memcpy(SaveCase, Case, (MaxCase + 1) * sizeof(DataRec));

  FindGlobalProperties();

  if (CHOOSEMODE)
    USEINSTANCES = true;

  /*  Set minimum target coverage for a rule as 1% of cases (to a
      maximum of 20).  However, it must be at least MINSPLIT and
      must not exceed cases / MAXRULES  */

  Cases = MaxCase + 1;

  MINITEMS = Min(20, rint(Cases / 100));

  if (MINITEMS > Cases / MAXRULES) {
    MINITEMS = Cases / MAXRULES;
  }

  if (MINITEMS < MINSPLIT) {
    MINITEMS = MINSPLIT;
  }

  Cttee = AllocZero(MEMBERS, RRuleSet);

  ForEach(m, 0, MEMBERS - 1) {

    Cttee[m] = ConstructRuleSet(m);

    memcpy(Case, SaveCase, (MaxCase + 1) * sizeof(DataRec)); /* restore */

    if (m < MEMBERS - 1) {
      /*  Adjust target value for next regression tree  */

      Err = 0;

      ForEach(i, 0, MaxCase) {
        PredVal(Case[i]) = RuleSetPrediction(Cttee[m], Case[i]);

        Err += fabs(Class(Case[i]) - PredVal(Case[i]));

        Class(Case[i]) = 2 * CVal(Case[i], ClassAtt) - PredVal(Case[i]);
      }

      SumErr += Err;
    }
  }

  FreeUnlessNil(SaveCase);
  SaveCase = Nil;

  if (!XVAL && MEMBERS > 1) {
    /*  Calculate the error reduction achieved by committee model  */

    SaveUSEINSTANCES = USEINSTANCES;
    USEINSTANCES = false;

    FindPredictedValues(Cttee, 0, MaxCase);

    USEINSTANCES = SaveUSEINSTANCES;

    ForEach(i, 0, MaxCase) {
      FinalErr += fabs(Class(Case[i]) - PredVal(Case[i]));
    }

    ErrReduction = FinalErr / (SumErr / (MEMBERS - 1));
  }

  /*  See whether to use rulesets or rulesets with instances  */

  if (USEINSTANCES) {
    MAXD = -1; /* causes InitialiseInstances to set it */

    InitialiseInstances(Cttee);
  }

  if (CHOOSEMODE) {
    CheckForms(Cttee);
  }

  if (!XVAL)
    SaveCommittee(Cttee, ".model");
}

RRuleSet ConstructRuleSet(int ModelNo)
/*       ----------------  */
{
  RRuleSet RS;
  char Msg[20];
  CaseNo i;
  RuleNo r;
  float TempMTSize;

  NotifyStage(GROUPDATA);
  Progress(-(MaxCase + 1.0));

  FormTree(0, MaxCase, 0, &TempMT, Nil);

  NotifyStage(ADDMODELS);
  Progress((TempMTSize = (float)-TreeSize(TempMT)));

  AddModels(0, MaxCase, TempMT, Nil);

  NotifyStage(SIMPLIFYGROUPS);
  Progress(TempMTSize);

  Prune(TempMT);
  AdjustAllThresholds(TempMT);
  Verbosity(1, PrintTree(TempMT, "Model tree"))

      NotifyStage(FORMRULES);
  Progress(-(MaxCase + 1.0));

  /*  Restore original target values  */

  ForEach(i, 0, MaxCase) { Class(Case[i]) = CVal(Case[i], ClassAtt); }

  RS = FormRules(TempMT);
  ForEach(r, 1, RS->SNRules) { RS->SRule[r]->MNo = ModelNo; }

  if (MEMBERS > 1) {
    sprintf(Msg, "Model %d:", ModelNo + 1);
  } else {
    sprintf(Msg, "Model:");
  }

  PrintRules(RS, Msg);

  FreeTree(TempMT);
  TempMT = Nil;

  return RS;
}

/*************************************************************************/
/*                                                                       */
/*      Check performance of model                                       */
/*                                                                       */
/*************************************************************************/

void EvaluateCttee(RRuleSet *Cttee, Boolean Details)
/*   -------------  */
{
  CaseNo i, MaxTest;
  double Real, CorCoeff = 0, Tests, AbsErr = 0, BaseAbsErr = 0, ProdVar,
               SumX = 0, SumY = 0, SumXY = 0, SumXX = 0, SumYY = 0;

  if (MaxCase < 0)
    return;

  MaxTest = MaxCase;

  if (USEINSTANCES) {
    if (Details) {
      /*  Copy instances to improve cache performance  */

      CopyInstances();
    } else if (MaxCase >= 2 * EVALSAMPLE) {
      /*  For composite models, use only a sample for evaluating large
          training sets  */

      SampleTrainingCases();
      MaxTest = EVALSAMPLE - 1;
    }
  }

  /*  Find the cases' predicted values if they are not already known  */

  if (Details || USEINSTANCES || MEMBERS == 1) {
    FindPredictedValues(Cttee, 0, MaxTest);
  }

  if (Details) {
    if (!(Pf = GetFile(".pred", "w")))
      Error(NOFILE, Fn, E_ForWrite);

    fprintf(Pf, T_Default, Precision + 1, GlobalMean);
    fprintf(Pf, F_Actual "  " F_Predicted "    " F_Case "\n" F_Value
                         "  " F_Value "\n"
                         " --------  ---------    " F_UCase "\n");
  }

  /*  Evaluate performance of model  */

  ForEach(i, 0, MaxTest) {
    Real = Class(Case[i]);

    AbsErr += fabs(Real - PredVal(Case[i]));
    BaseAbsErr += fabs(Real - GlobalMean);

    SumX += Real;
    SumXX += Real * Real;
    SumY += PredVal(Case[i]);
    SumYY += PredVal(Case[i]) * PredVal(Case[i]);
    SumXY += Real * PredVal(Case[i]);

    if (Details) {
      fprintf(Pf, "%9.*f  %9.*f    %s\n", Precision, Real, Precision + 1,
              PredVal(Case[i]), CaseLabel(i));
    }

    Progress(1.0);
  }

  if (Details) {
    fclose(Pf);
    Pf = 0;
  }

  Tests = MaxTest + 1;

  ProdVar = (SumXX - SumX * SumX / Tests) * (SumYY - SumY * SumY / Tests);
  if (ProdVar > 0) {
    CorCoeff = (SumXY - SumX * SumY / Tests) / sqrt(ProdVar);
  }

  fprintf(Of, "\n");
  fprintf(Of, F_AvErr "%10.*f\n", Precision + 1, AbsErr / Tests);
  fprintf(Of, F_RelErr "%10.2f\n", (BaseAbsErr ? AbsErr / BaseAbsErr : 1.0));
  fprintf(Of, F_CorrCoeff "%10.2f\n", Max(0, CorCoeff));

  /*  Summarise attribute usage on training data  */

  if (!Details) {
    AttributeUsage();
  }
}

/*************************************************************************/
/*                                                                       */
/*      Sample EVALSAMPLE cases from training set    */
/*                                                                       */
/*************************************************************************/

void SampleTrainingCases(void)
/*   -------------------  */
{
  CaseNo i, j;
  double Step;
  DataRec xab;

  Step = (MaxCase + 1) / (double)EVALSAMPLE;
  ForEach(i, 1, EVALSAMPLE - 1) {
    j = i * Step;
    Swap(i, j);
  }
}

/*************************************************************************/
/*                                                                       */
/*      Report attribute usage in conditions and models    */
/*                                                                       */
/*************************************************************************/

CaseCount SumCases, *SumCond = 0, *SumModel = 0;
Boolean *AttUsed = 0;

void AttributeUsage(void)
/*   --------------  */
{
  RRuleSet RS;
  int m;
  RuleNo r;
  Attribute Att, BestAtt;
  char U1[5], U2[5];

  /*  Initialise counts  */

  SumCases = 0;
  SumCond = AllocZero(MaxAtt + 1, CaseCount);
  SumModel = AllocZero(MaxAtt + 1, CaseCount);
  AttUsed = Alloc(MaxAtt + 1, Boolean);

  /*  Scan rules in committee  */

  ForEach(m, 0, MEMBERS - 1) {
    RS = Cttee[m];

    ForEach(r, 1, RS->SNRules) { UpdateUsage(RS->SRule[r]); }
  }

  /*  Show attributes in order of combined usage  */

  fprintf(Of, T_AttUsage);

  while (true) {
    BestAtt = 0;

    ForEach(Att, 1, MaxAtt) {
      if (Max(SumCond[Att], SumModel[Att]) >= 0.01 * SumCases &&
          (!BestAtt || SumCond[Att] > SumCond[BestAtt] ||
           (SumCond[Att] >= SumCond[BestAtt] &&
            SumModel[Att] > SumModel[BestAtt]))) {
        BestAtt = Att;
      }
    }

    if (!BestAtt)
      break;

    sprintf(U1, "%3.0f%%", rint((100.0 * SumCond[BestAtt]) / SumCases));
    sprintf(U2, "%3.0f%%", rint((100.0 * SumModel[BestAtt]) / SumCases));

    fprintf(Of, "\t  %4s   %4s    %s\n",
            (SumCond[BestAtt] >= 0.01 * SumCases ? U1 : " "),
            (SumModel[BestAtt] >= 0.01 * SumCases ? U2 : " "),
            AttName[BestAtt]);

    SumCond[BestAtt] = SumModel[BestAtt] = 0;
  }

  Free(SumCond);
  Free(SumModel);
  Free(AttUsed);
}

void UpdateUsage(CRule R)
/*   -----------  */
{
  Attribute Att;
  int d;

  SumCases += R->Cover;

  /*  Attributes used in conditions.  Must assemble in table in case
      same attribute appears more than once  */

  memset(AttUsed, false, MaxAtt + 1);

  ForEach(d, 1, R->Size) { NoteUsed(R->Lhs[d]->Tested); }

  ForEach(Att, 1, MaxAtt) {
    if (AttUsed[Att])
      SumCond[Att] += R->Cover;
  }

  /*  Attributes used in model  */

  memset(AttUsed, false, MaxAtt + 1);

  ForEach(Att, 1, MaxAtt) {
    if (R->Rhs[Att])
      NoteUsed(Att);
  }

  ForEach(Att, 1, MaxAtt) {
    if (AttUsed[Att])
      SumModel[Att] += R->Cover;
  }
}

void NoteUsed(Attribute Att)
/*   --------  */
{
  int i;

  if (AttUsed[Att])
    return;

  AttUsed[Att] = true;

  if (AttDef[Att]) {
    /*  Include attributes that appear in definition  */

    ForEach(i, 1, AttDefUses[Att][0]) { NoteUsed(AttDefUses[Att][i]); }
  }
}
