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
/*            */
/* Miscellaneous routines for rule handling      */
/* ----------------------------------------      */
/*            */
/*************************************************************************/

#include "defns.h"
#include "extern.h"

#include "redefine.h"
#include "transform.h"

/*************************************************************************/
/*            */
/* Add a new rule to the current ruleset, by updating Rule[],    */
/* NRules and, if necessary, RuleSpace       */
/*            */
/*************************************************************************/

Boolean NewRule(Condition Cond[], int NCond, Boolean *Deleted, CaseCount Cover,
                float Mean, float LoVal, float HiVal, float EstErr,
                double *Model)
/*      -------  */
{
  int d, dd, id, r, Size = 0, Bytes;
  CRule R;
  Condition *Lhs;
  Boolean Exclude = false;
  float Range, V;
  extern double *Total;

  /*  Sort and copy the conditions  */

  ForEach(d, 1, NCond) {
    if (!Deleted[d])
      Size++;
  }

  Lhs = Alloc(Size + 1, Condition);

  ForEach(d, 1, Size) {
    dd = 0;
    ForEach(id, 1, NCond) {
      if (!Deleted[id] && (!dd || Total[id] > Total[dd])) {
        dd = id;
      }
    }

    Lhs[d] = Alloc(1, CondRec);
    memcpy(Lhs[d], Cond[dd], sizeof(CondRec));

    if (Lhs[d]->NodeType == BrSubset) {
      Bytes = (MaxAttVal[Lhs[d]->Tested] >> 3) + 1;
      Lhs[d]->Subset = Alloc(Bytes, unsigned char);
      memcpy(Lhs[d]->Subset, Cond[dd]->Subset, Bytes);
    }

    Deleted[dd] = true;
  }

  /*  See if rule already exists  */

  for (r = 1; !Exclude && r <= NRules; r++) {
    if (SameRule(r, Lhs, Size)) {
      Verbosity(1, fprintf(Of, "\tduplicates rule %d\n", r)) Exclude = true;

      /*  Save this model if has lower estimated error  */

      if (EstErr < Rule[r]->EstErr) {
        memcpy(Rule[r]->Rhs, Model, (MaxAtt + 1) * sizeof(double));
        Rule[r]->EstErr = EstErr;
      }
    }
  }

  if (Exclude) {
    /*  Free any subsets  */

    ForEach(d, 1, Size) {
      if (Lhs[d]->NodeType == BrSubset) {
        FreeUnlessNil(Lhs[d]->Subset);
      }
    }

    FreeVector((void **)Lhs, 1, Size);

    return false;
  }

  /*  Make sure there is enough room for the new rule  */

  NRules++;
  if (NRules >= RuleSpace) {
    RuleSpace += 100;
    if (RuleSpace > 100) {
      Realloc(Rule, RuleSpace, CRule);
    } else {
      Rule = Alloc(RuleSpace, CRule);
    }
  }

  /*  Form the new rule  */

  Rule[NRules] = R = Alloc(1, RuleRec);

  R->RNo = NRules;
  R->Size = Size;
  R->Lhs = Lhs;

  R->Cover = Cover;
  R->Mean = Mean;
  R->LoVal = LoVal;
  R->HiVal = HiVal;

  Range = HiVal - LoVal;
  R->LoLim = ((V = R->LoVal - EXTRAP * Range) < 0 && R->LoVal >= 0 ? 0 : V);
  R->HiLim = ((V = R->HiVal + EXTRAP * Range) > 0 && R->HiVal <= 0 ? 0 : V);

  R->Rhs = AllocZero(MaxAtt + 1, double);
  memcpy(R->Rhs, Model, (MaxAtt + 1) * sizeof(double));

  R->EstErr = EstErr;

  Verbosity(1, PrintRule(R))

      return true;
}

/*************************************************************************/
/*            */
/*  Decide whether the given rule duplicates rule r      */
/*            */
/*************************************************************************/

Boolean SameRule(RuleNo r, Condition Cond[], int NConds)
/*      --------  */
{
  int d, i, Bytes;

  if (Rule[r]->Size != NConds) {
    return false;
  }

  ForEach(d, 1, NConds) {
    if (Rule[r]->Lhs[d]->NodeType != Cond[d]->NodeType ||
        Rule[r]->Lhs[d]->Tested != Cond[d]->Tested) {
      return false;
    }

    switch (Cond[d]->NodeType) {
    case BrDiscr:
      if (Rule[r]->Lhs[d]->TestValue != Cond[d]->TestValue) {
        return false;
      }
      break;

    case BrThresh:
      if (Rule[r]->Lhs[d]->TestValue != Cond[d]->TestValue ||
          Rule[r]->Lhs[d]->Cut != Cond[d]->Cut) {
        return false;
      }
      break;

    case BrSubset:
      Bytes = (MaxAttVal[Cond[d]->Tested] >> 3) + 1;
      ForEach(i, 0, Bytes - 1) {
        if (Rule[r]->Lhs[d]->Subset[i] != Cond[d]->Subset[i]) {
          return false;
        }
      }
    }
  }

  return true;
}

/*************************************************************************/
/*            */
/* Free space occupied by a rule or a committee    */
/*            */
/*************************************************************************/

void ReleaseRule(CRule R)
/*   -----------  */
{
  int d;

  ForEach(d, 1, R->Size) {
    if (R->Lhs[d]->NodeType == BrSubset) {
      FreeUnlessNil(R->Lhs[d]->Subset);
    }
    FreeUnlessNil(R->Lhs[d]);
  }
  FreeUnlessNil(R->Lhs);
  FreeUnlessNil(R->Rhs);
  FreeUnlessNil(R);
}

void FreeCttee(RRuleSet *Cttee)
/*   ---------  */
{
  int m, r;
  RRuleSet RS;

  ForEach(m, 0, MEMBERS - 1) {
    if (!(RS = Cttee[m]))
      continue;

    ForEach(r, 1, RS->SNRules) { ReleaseRule(RS->SRule[r]); }
    Free(RS->SRule);
    Free(RS);
  }

  Free(Cttee);
}

/*************************************************************************/
/*            */
/* Print a ruleset        */
/*            */
/*************************************************************************/

void PrintRules(RRuleSet RS, String Msg)
/*   ----------  */
{
  int r;

  fprintf(Of, "\n%s\n", Msg);

  ForEach(r, 1, RS->SNRules) { PrintRule(RS->SRule[r]); }
}

/*************************************************************************/
/*            */
/* Print the rule R         */
/*            */
/*************************************************************************/

void PrintRule(CRule R)
/*   ---------  */
{
  int c, d, dd, id, LineLen, EntryLen, Indent, NCoeff = 0;
  Attribute Att;
  char Entry[1000];
  double *Model;
  float *Importance;

  if (MEMBERS > 1) {
    fprintf(Of, "\n  " T_Rule " %d/%d", R->MNo + 1, R->RNo);
  } else {
    fprintf(Of, "\n  " T_Rule " %d", R->RNo);
  }
  fprintf(Of, TX_RInfo(R->Cover, Precision + 1, R->Mean, R->LoVal, R->HiVal,
                       R->EstErr));

  if (R->Size) {
    fprintf(Of, "    " T_If "\n");

    /*  Mark all conditions as unprinted or-ing flag to NodeType  */

    ForEach(d, 1, R->Size) { R->Lhs[d]->NodeType |= 8; }

    ForEach(d, 1, R->Size) {
      dd = 0;
      ForEach(id, 1, R->Size) {
        if ((R->Lhs[id]->NodeType & 8) &&
            (!dd || Before(R->Lhs[id], R->Lhs[dd]))) {
          dd = id;
        }
      }

      R->Lhs[dd]->NodeType &= 7;
      PrintCondition(R->Lhs[dd]);
    }

    fprintf(Of, "    " T_Then "\n");
  }

  /*  Print the model.  First estimate the importance of the coefficients  */

  Model = R->Rhs;

  Importance = AllocZero(MaxAtt + 1, float);
  ForEach(Att, 1, MaxAtt) {
    if (Att != ClassAtt && Model[Att]) {
      Importance[Att] = fabs(Model[Att]) * AttSD[Att];
      NCoeff++;
    }
  }

  sprintf(Entry, "%s =", AttName[ClassAtt]);
  Indent = CharWidth(Entry);

  sprintf(Entry + Indent, " %.14g", Model[0]);
  fprintf(Of, "\t%s", Entry);
  LineLen = CharWidth(Entry);

  ForEach(c, 1, NCoeff) {
    /*  Select the next attribute to print  */

    Att = 1;
    ForEach(d, 2, MaxAtt) {
      if (Importance[d] > Importance[Att])
        Att = d;
    }
    Importance[Att] = 0;

    /*  Print, breaking lines when necessary  */

    sprintf(Entry, " %c %.14g %s", (Model[Att] > 0 ? '+' : '-'),
            fabs(Model[Att]), AttName[Att]);
    EntryLen = CharWidth(Entry);

    if (LineLen + EntryLen > 72) {
      fprintf(Of, "\n\t%*s", Indent, " ");
      LineLen = Indent;
    }
    fprintf(Of, "%s", Entry);
    LineLen += EntryLen;
  }
  fprintf(Of, "\n");
  Free(Importance);
}

/*************************************************************************/
/*            */
/* Print a condition C of a rule        */
/*            */
/*************************************************************************/

void PrintCondition(Condition C)
/*  --------------  */
{
  DiscrValue v, pv, Last, Values = 0;
  Boolean First = true;
  Attribute Att;
  int Col, Base, Entry;
  char CVS[20];

  v = C->TestValue;
  Att = C->Tested;

  fprintf(Of, "\t%s", AttName[Att]);

  if (v < 0) {
    fprintf(Of, T_IsUnknown);
    return;
  }

  switch (C->NodeType) {
  case BrDiscr:
    fprintf(Of, " = %s\n", AttValName[Att][v]);
    break;

  case BrThresh:
    if (v == 1) {
      fprintf(Of, " = N/A\n");
    } else {
      CValToStr(C->Cut, Att, CVS);
      fprintf(Of, " %s %s\n", (v == 2 ? "<=" : ">"), CVS);
    }
    break;

  case BrSubset:
    /*  Count values at this branch  */

    ForEach(pv, 1, MaxAttVal[Att]) {
      if (In(pv, C->Subset)) {
        Last = pv;
        Values++;
      }
    }

    if (Values == 1) {
      fprintf(Of, " = %s\n", AttValName[Att][Last]);
      break;
    }

    if (Ordered(Att)) {
      /*  Find first value  */

      for (pv = 1; !In(pv, C->Subset); pv++)
        ;

      fprintf(Of, " " T_InRange " [%s-%s]\n", AttValName[Att][pv],
              AttValName[Att][Last]);
      break;
    }

    /*  Must keep track of position to break long lines  */

    fprintf(Of, " %s {", T_ElementOf);
    Col = Base = CharWidth(AttName[Att]) + CharWidth(T_ElementOf) + 11;

    ForEach(pv, 1, MaxAttVal[Att]) {
      if (In(pv, C->Subset)) {
        Entry = CharWidth(AttValName[Att][pv]);

        if (First) {
          First = false;
        } else if (Col + Entry + 2 >= Width) {
          Col = Base;
          fprintf(Of, ",\n%*s", Col, "");
        } else {
          fprintf(Of, ", ");
          Col += 2;
        }

        fprintf(Of, "%s", AttValName[Att][pv]);
        Col += Entry;
      }
    }
    fprintf(Of, "}\n");
  }
}

/*************************************************************************/
/*            */
/* Check whether a case satisfies a condition    */
/*            */
/*************************************************************************/

Boolean Satisfies(DataRec CaseDesc, Condition OneCond)
/*      ---------  */
{
  DiscrValue v;
  ContValue cv;
  DiscrValue Outcome;
  Attribute Att;

  Att = OneCond->Tested;

  /*  Determine the outcome of this test on this item  */

  switch (OneCond->NodeType) {
  case BrDiscr: /* test of discrete attribute */

    v = DVal(CaseDesc, Att);
    Outcome = (v == 0 ? -1 : v);
    break;

  case BrThresh: /* test of continuous attribute */

    cv = CVal(CaseDesc, Att);
    Outcome = (NotApplic(CaseDesc, Att) ? 1 : cv <= OneCond->Cut ? 2 : 3);
    break;

  case BrSubset: /* subset test on discrete attribute  */

    v = DVal(CaseDesc, Att);
    Outcome =
        (v <= MaxAttVal[Att] && In(v, OneCond->Subset) ? OneCond->TestValue
                                                       : 0);
  }

  return (Outcome == OneCond->TestValue);
}
