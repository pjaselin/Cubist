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

double AverageDev(float Mean, CaseNo Fp, CaseNo Lp)
/*     ----------  */
{
  double Wt, SumWt = 0, Sum = 0;
  CaseNo i;

  ForEach(i, Fp, Lp) {
    Wt = CWeight(Case[i]);

    SumWt += Wt;
    Sum += Wt * fabs(Mean - Class(Case[i]));
  }

  return Sum / SumWt;
}

double SD(double N, double Sum, double SumSq)
/*     --  */
{
  return (N < 2 ? GlobalSD : sqrt((SumSq - Sum * Sum / N + 1E-3) / (N - 1)));
}

double AverageErr(DataRec *D, CaseNo Fp, CaseNo Lp, double *Model)
/*     ----------  */
{
  CaseNo i;
  double Wt, Sum = 0, SumWt = 0;

  FindModelAtts(Model);

  ForEach(i, Fp, Lp) {
    Wt = CWeight(Case[i]);

    Sum += Wt * fabs(Class(D[i]) - LinModel(Model, D[i]));
    SumWt += Wt;
  }

  return Sum / SumWt;
}

double ComputeGain(Tree Node)
/*     -----------  */
{
  double Resid = 0, Cases = 0;
  DiscrValue v;

  ForEach(v, 1, 3) {
    Cases += GEnv.BrFreq[v];
    Resid +=
        GEnv.BrFreq[v] * SD(GEnv.BrFreq[v], GEnv.BrSum[v], GEnv.BrSumSq[v]);
  }

  return Node->SD - Resid / Cases;
}

double EstimateErr(double Val, double NData, float NParam)
/*     -----------  */
{
  if (NParam >= NData)
    NParam = NData - 1;

  return Val * (NData + NParam) / (NData - NParam);
}
