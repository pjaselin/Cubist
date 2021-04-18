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
/*                                                                */
/* Predict the value of a case from a ruleset    */
/* ------------------------------------------    */
/*                                                                */
/*************************************************************************/

#include "defns.h"
#include "extern.h"

#include "redefine.h"
#include "transform.h"

/*************************************************************************/
/*                                                                */
/* Find rules that apply to case and form average    */
/*                                                                */
/*************************************************************************/

float PredictValue(RRuleSet *Cttee, DataRec CaseDesc)
/*    ------------  */
{
  double PredSum = 0;
  int m;

  ForEach(m, 0, MEMBERS - 1) {
    PredSum += RuleSetPrediction(Cttee[m], CaseDesc);
  }

  return PredSum / MEMBERS;
}

float RuleSetPrediction(RRuleSet RS, DataRec CaseDesc)
/*    -----------------  */
{
  double Sum = 0, Weight = 0, Val;
  int r;
  CRule R;
  Attribute Att;

  ForEach(r, 1, RS->SNRules) {
    R = RS->SRule[r];

    if (Matches(R, CaseDesc)) {
      /*  Evaluate RHS.  Cannot use RawLinModel() because
          have not run FindModelAtts()  */

      Val = R->Rhs[0];
      ForEach(Att, 1, MaxAtt) { Val += CVal(CaseDesc, Att) * R->Rhs[Att]; }

      Sum += (Val < R->LoLim ? R->LoLim : Val > R->HiLim ? R->HiLim : Val);
      Weight += 1.0;
    }
  }

  if (Weight) {
    return Sum / Weight;
  } else {
    return GlobalMean;
  }
}

/*************************************************************************/
/*                 */
/* Determine whether a case satisfies all conditions of a rule  */
/*                 */
/*************************************************************************/

Boolean Matches(CRule R, DataRec Case)
/*      -------  */
{
  int d;

  ForEach(d, 1, R->Size) {
    if (!Satisfies(Case, R->Lhs[d])) {
      return false;
    }
  }

  return true;
}

/*************************************************************************/
/*                 */
/* Evaluate a linear model on a case     */
/*                 */
/*************************************************************************/

float RawLinModel(double *Model, DataRec Case)
/*    -----------  */
{
  double Sum;
  Attribute Att, a;

  Sum = Model[0];
  ForEach(a, 1, GEnv.NModelAtt) {
    Att = GEnv.ModelAtt[a];
    Sum += Model[Att] * CVal(Case, Att);
  }

  return Sum;
}

float LinModel(double *Model, DataRec Case)
/*    --------  */
{
  float Raw;

  Raw = RawLinModel(Model, Case);

  return (Raw < Floor ? Floor : Raw > Ceiling ? Ceiling : Raw);
}

/*************************************************************************/
/*                                                                       */
/* Find values predicted by a model for cases Fp to Lp.   */
/*                                                                       */
/*************************************************************************/

void FindPredictedValues(RRuleSet *Cttee, CaseNo Fp, CaseNo Lp)
/*   -------------------  */
{
  CaseNo i;

  ForEach(i, Fp, Lp) {
    PredVal(Case[i]) = (USEINSTANCES ? NNEstimate(Cttee, Case[i])
                                     : PredictValue(Cttee, Case[i]));
  }
}
