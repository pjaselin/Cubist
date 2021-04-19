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
/* Carry out cross validation trials     */
/* ---------------------------------     */
/*                                                                       */
/*************************************************************************/

#include "defns.h"
#include "extern.h"

#include "redefine.h"
#include "transform.h"

/*************************************************************************/
/*                                                                       */
/* Outer function (differs from xval script)    */
/*                                                                       */
/*************************************************************************/

void CrossVal(void)
/*   --------  */
{
  CaseNo i, Size, Start = 0, Next, N;
  int f, SmallTestBlocks;
  double *ErrMag, R, SumR = 0, SumRR = 0, /* real value */
      P, SumP = 0, SumPP = 0,             /* predicted value */
      SumRP = 0,                          /* for correlation coeff */
      M, SumM = 0,                        /* error magnitude */
      D, SumD = 0,                        /* default error magnitude */
      TrainingMean;

  if (FOLDS > MaxCase + 1) {
    fprintf(Of, T_FoldsReduced);
    FOLDS = MaxCase + 1;
  }

  ErrMag = AllocZero(FOLDS, double);
  Blocked = Alloc(MaxCase + 1, DataRec);
  SaveMaxCase = MaxCase;

  Prepare();

  if (!(Pf = GetFile(".pred", "w")))
    Error(0, Fn, E_ForWrite);

  /*  First test blocks may be smaller than the others  */

  SmallTestBlocks = FOLDS - ((MaxCase + 1) % FOLDS);
  Size = (MaxCase + 1) / FOLDS;

  ForEach(f, 0, FOLDS - 1) {
    fprintf(Of, "\n\n[ " T_Fold " %d ]\n", f + 1);

    if (f == SmallTestBlocks)
      Size++;
    MaxCase = SaveMaxCase - Size;

    /*  Copy blocks back into Case:
            train: 0 to MaxCase
            test:  MaxCase+1 to SaveMaxCase  */

    Next = Start;
    ForEach(i, 0, SaveMaxCase) {
      Case[i] = Blocked[Next];
      Next = (Next + 1) % (SaveMaxCase + 1);
    }
    Start = (Start + MaxCase + 1) % (SaveMaxCase + 1);

    TrainingMean = 0;
    ForEach(i, 0, MaxCase) { TrainingMean += Class(Case[i]); }
    TrainingMean /= MaxCase + 1;

    ConstructCttee();

    /*  Record size and errors  */

    FindPredictedValues(Cttee, MaxCase + 1, SaveMaxCase);

    fprintf(Pf, "\n(Default value %.*f)\n\n", Precision + 1, GlobalMean);
    fprintf(Pf, "   Actual  Predicted    Case\n"
                "    Value      Value\n"
                " --------  ---------    ----\n");

    ForEach(i, MaxCase + 1, SaveMaxCase) {
      R = Class(Case[i]);
      P = PredVal(Case[i]);
      ErrMag[f] += (M = fabs(Class(Case[i]) - P));
      D = fabs(R - TrainingMean);

      fprintf(Pf, "%9.*f  %9.*f    %s\n", Precision, R, Precision + 1, P,
              CaseLabel(i));

      /*  Statistics for PVE, correlation coefficient */

      SumM += M;
      SumR += R;
      SumRR += R * R;
      SumP += P;
      SumPP += P * P;
      SumRP += R * P;
      SumD += D;
    }
    ErrMag[f] /= Size;

    fprintf(Of, T_EvalHoldOut "\n    " T_MeanErrMag "  %.*f\n", Size,
            Precision + 1, ErrMag[f]);

    /*  Free space used by rulesets  */

    FreeCttee(Cttee);
    Cttee = Nil;

    if (USEINSTANCES) {
      FreeInstances();
    }
  }

  fclose(Pf);
  Pf = 0;

  /*  Print summary of cross-validation  */

  MaxCase = SaveMaxCase;
  N = MaxCase + 1;

  fprintf(Of, "\n\n" T_Summary ":\n\n");
  fprintf(Of, F_AvErr "%10.*f\n", Precision + 1, SumM / N);
  fprintf(Of, F_RelErr "      %4.2f\n", (SumD ? SumM / SumD : 0.0));
  fprintf(
      Of, F_CorrCoeff "      %4.2f\n",
      (SumRP - SumR * SumP / N) /
          (sqrt((SumRR - SumR * SumR / N) * (SumPP - SumP * SumP / N)) + 1E-6));

  /*  Free local storage  */

  ForEach(i, 0, MaxCase) { Case[i] = Blocked[i]; }

  Free(ErrMag);
  Free(Blocked);
  Blocked = Nil;
}

/*************************************************************************/
/*                                                                       */
/*      Prepare data for cross-validation     */
/*                                                                       */
/*************************************************************************/

void Prepare(void)
/*   -------  */
{
  CaseNo i, First = 0, Last, *Temp, Hold, Next = 0;
  int Bin, Group;
  ContValue MinVal, MaxVal, Range;

  Temp = Alloc(MaxCase + 1, CaseNo);
  ForEach(i, 0, MaxCase) { Temp[i] = i; }

  Shuffle(Temp);

  /*  Find maximum and minimum class value  */

  MaxVal = MinVal = Class(Case[0]);
  ForEach(i, 1, MaxCase) {
    if (Class(Case[i]) < MinVal)
      MinVal = Class(Case[i]);
    else if (Class(Case[i]) > MaxVal)
      MaxVal = Class(Case[i]);
  }
  Range = MaxVal - MinVal;

  /*  Sort into groups of approximately the same value  */

  ForEach(Bin, 0, 9) {
    Last = First - 1;

    ForEach(i, First, MaxCase) {
      Group = Min(9, 10 * (Class(Case[Temp[i]]) - MinVal) / Range);

      if (Group == Bin) {
        Last++;
        Hold = Temp[Last];
        Temp[Last] = Temp[i];
        Temp[i] = Hold;
      }
    }

    First = Last + 1;
  }

  /*  Organize into stratified blocks  */

  ForEach(First, 0, FOLDS - 1) {
    for (i = First; i <= MaxCase; i += FOLDS) {
      Blocked[Next++] = Case[Temp[i]];
    }
  }

  Free(Temp);
}

/*************************************************************************/
/*                                                                       */
/*      Shuffle the data items                                           */
/*                                                                       */
/*************************************************************************/

void Shuffle(int *Vec)
/*   -------  */
{
  int This = 0, Alt, Left = MaxCase + 1, Hold;

  ResetKR(KRInit);

  while (Left) {
    Alt = This + (Left--) * KRandom();

    Hold = Vec[This];
    Vec[This++] = Vec[Alt];
    Vec[Alt] = Hold;
  }
}
