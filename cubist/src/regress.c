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
/* Find best-fit linear model by matrix inversion    */
/* ----------------------------------------------    */
/* This code includes extensions to the standard methodology,  */
/* principally model simplification and outlier elimination  */
/*                                                                       */
/*************************************************************************/

#include "defns.h"
#include "extern.h"

#include "redefine.h"
#include "transform.h"

/* x[i][v] = data (in Case) */
/* y[i]    = dependent var (in Class) */
/* least-squares solution given by xTx.Model = xTy  */

/*************************************************************************/
/*                                                                       */
/* Find regression model for items Fp through Lp.    */
/*      Do not use variables in GEnv.DoNotUse.     */
/*                                                                       */
/*************************************************************************/

void Regress(CaseNo Fp, CaseNo Lp, double *Model)
/*   -------  */
{
  CaseNo i, Kp;
  int j, jj, k, kk;
  ContValue ClassVal, JVal;
  double Val, SumR = 0, Bias = 0, AvResid, Wt, Cases = 0;
  Attribute a, Att;
  Boolean First;

  /*  Find candidate attributes  */

  GEnv.NModelAtt = 0;
  GEnv.ModelAtt[0] = 0;

  GEnv.Mean[0] = GEnv.Var[0] = Model[0] = GEnv.AvDev[0] = 0;
  GEnv.ZeroCoeff[0] = false;

  ForEach(Att, 1, MaxAtt) {
    if (Continuous(Att) && Att != ClassAtt && !Skip(Att) &&
        (!GEnv.DoNotUse || !GEnv.DoNotUse[Att])) {
      GEnv.ModelAtt[++GEnv.NModelAtt] = Att;
      GEnv.Mean[Att] = GEnv.Var[Att] = Model[Att] = GEnv.AvDev[Att] = 0;
      GEnv.ZeroCoeff[Att] = false;
    } else {
      GEnv.ZeroCoeff[Att] = true;
    }
  }

  /*  Find means and variances in one data pass  */

  ForEach(i, Fp, Lp) {
    Wt = CWeight(Case[i]);
    Cases += Wt;

    ForEach(a, 0, GEnv.NModelAtt) {
      Att = GEnv.ModelAtt[a];

      if (a > 0 && NotApplic(Case[i], Att)) {
        GEnv.ZeroCoeff[Att] = true;
        GEnv.ModelAtt[a--] = GEnv.ModelAtt[GEnv.NModelAtt--];
      } else {
        GEnv.Mean[Att] += Wt * (Val = CVal(Case[i], Att));
        GEnv.Var[Att] += Wt * Val * Val;
      }
    }
  }

  GEnv.Mean[0] /= Cases;
  ForEach(a, 1, GEnv.NModelAtt) {
    Att = GEnv.ModelAtt[a];

    GEnv.Mean[Att] /= Cases;
    GEnv.Var[Att] =
        (GEnv.Var[Att] - Cases * GEnv.Mean[Att] * GEnv.Mean[Att]) / (Cases - 1);

    if (GEnv.Var[Att] < 1E-6) {
      GEnv.ZeroCoeff[Att] = true;
      GEnv.ModelAtt[a--] = GEnv.ModelAtt[GEnv.NModelAtt--];
    }
  }

  /*  Now find average deviations in another data pass  */

  ForEach(i, Fp, Lp) {
    Wt = CWeight(Case[i]);

    ForEach(a, 0, GEnv.NModelAtt) {
      Att = GEnv.ModelAtt[a];

      GEnv.AvDev[Att] += Wt * fabs(CVal(Case[i], Att) - GEnv.Mean[Att]);
    }
  }

  ForEach(a, 0, GEnv.NModelAtt) {
    Att = GEnv.ModelAtt[a];

    GEnv.AvDev[Att] /= Cases;
  }

  /*  Don't attempt to form model if there are no possible coefficients
      or if items < 2 * possible coefficients  */

  if (GEnv.NModelAtt < 1 || Cases < 2 * GEnv.NModelAtt) {
    Model[0] = GEnv.Mean[0];
    ForEach(Att, 1, MaxAtt) { Model[Att] = 0; }

    return;
  }

  /*  Form linear model by matrix inversion  */

  BuildTables(Fp, Lp);
  Solve(Model);
  SimplifyModel(Case, Fp, Lp, Model);

  /*  See whether ought to exclude outliers and try again.
      An outlier wrt the linear model is a case whose residual
      error magnitude is more than five times the average  */

  FindModelAtts(Model);
  if (!GEnv.NModelAtt)
    return; /* just a mean */

  /*  Compute the residuals and correct any bias caused by limiting
      predictions to range [Floor, Ceiling]  */

  ForEach(i, Fp, Lp) {
    Wt = CWeight(Case[i]);
    GEnv.Resid[i] = Class(Case[i]) - LinModel(Model, Case[i]);
    SumR += Wt * fabs(GEnv.Resid[i]);
    Bias += Wt * GEnv.Resid[i];
  }
  AvResid = SumR / Cases;
  Model[0] += Bias / Cases;

  Kp = Fp - 1;
  First = true;

  ForEach(i, Fp, Lp) {
    if (fabs(GEnv.Resid[i]) > 5 * AvResid) {
      /*  If this is the first outlier, re-initialise active
          attributes and preserve case order  */

      if (First) {
        FindActiveAtts();
        First = false;
      }

      /*  Remove contribution of this case  */

      Wt = CWeight(Case[i]);

      GEnv.xTx[0][0] -= Wt;
      GEnv.xTy[0] -= Wt * (ClassVal = Class(Case[i]));

      ForEach(jj, 1, GEnv.NModelAtt) {
        j = GEnv.ModelAtt[jj];
        GEnv.xTy[j] -= Wt * (JVal = CVal(Case[i], j)) * ClassVal;

        GEnv.xTx[j][0] -= Wt * JVal;

        ForEach(kk, 1, jj) {
          k = GEnv.ModelAtt[kk];
          GEnv.xTx[j][k] -= Wt * JVal * CVal(Case[i], k);
        }
      }
    } else {
      /*  Keep this case  */

      GEnv.Filtered[++Kp] = Case[i];
    }
  }

  /*  Rebuild if there are outliers.  */

  if (Kp < Lp) {
    Verbosity(1, fprintf(Of, "(Exclude %d outliers)\n", Lp - Kp))

        /*  Construct new model with outliers excluded.  Tables
            GEnv.xTx and GEnv.xTy do not need to be regenerated  */

        Solve(Model);
    SimplifyModel(GEnv.Filtered, Fp, Kp, Model);
  }
}

/*************************************************************************/
/*                                                                       */
/* Scan data to form GEnv.xTx and GEnv.xTy     */
/*                                                                       */
/*************************************************************************/

void BuildTables(CaseNo Fp, CaseNo Lp)
/*   -----------  */
{
  int i, j, jj, k, kk;
  ContValue ClassVal, JVal;
  double Wt;

  FindActiveAtts();

  /*  Initialise GEnv.xTx and GEnv.xTy  */

  ForEach(jj, 0, GEnv.NModelAtt) {
    j = GEnv.ModelAtt[jj];
    GEnv.xTy[j] = 0;

    ForEach(kk, 0, jj) { GEnv.xTx[j][GEnv.ModelAtt[kk]] = 0; }
  }

  /*  Evaluate GEnv.xTx[j][k] etc. for k <= j;  j=0 and k=0 are
      handled as special cases.
      (This loop has been reorganised to minimize cache misses
      that seem to be very important for Suns and AMD Athlons.)  */

  GEnv.xTx[0][0] = 0;

  ForEach(i, Fp, Lp) {
    Wt = CWeight(Case[i]);

    GEnv.xTx[0][0] += Wt;

    GEnv.xTy[0] += Wt * (ClassVal = Class(Case[i]));

    ForEach(jj, 1, GEnv.NModelAtt) {
      j = GEnv.ModelAtt[jj];
      GEnv.xTy[j] += Wt * (JVal = CVal(Case[i], j)) * ClassVal;

      GEnv.xTx[j][0] += Wt * JVal;

      ForEach(kk, 1, jj) {
        k = GEnv.ModelAtt[kk];
        GEnv.xTx[j][k] += Wt * JVal * CVal(Case[i], k);
      }
    }
  }
}

/*************************************************************************/
/*                                                                       */
/* Solve normal equations by matrix inversion.    */
/* Tables xTx and xTy are copied since we will need them again  */
/* during model simplification and if outliers are excluded  */
/*                                                                       */
/*************************************************************************/

void Solve(double *Model)
/*   -----  */
{
  int j, k, jj, max;
  double Pivot, MinPivot, MaxElt, Try;
  Boolean Singular = false;

  if (!GEnv.NModelAtt) {
    Model[0] = GEnv.xTy[0] / GEnv.xTx[0][0];

    ForEach(j, 1, MaxAtt) { Model[j] = 0; }

    return;
  }

  /*  Set up (destructible) copies A and B using only active attributes  */

  ForEach(j, 0, GEnv.NModelAtt) {
    ForEach(k, 0, j) {
      GEnv.A[j][k] = GEnv.A[k][j] =
          GEnv.xTx[GEnv.ModelAtt[j]][GEnv.ModelAtt[k]];
    }
    GEnv.B[j] = GEnv.xTy[GEnv.ModelAtt[j]];
  }

  /*  Construct inverse  */

  ForEach(j, 0, GEnv.NModelAtt) {
    /*  Find best pivot for column j.  First, find max value in
        original column j, and use that to estimate minimum
        acceptable pivot = maximum expected rounding error  */

    jj = GEnv.ModelAtt[j];
    MaxElt = 0;
    ForEach(k, 0, j) {
      if ((Try = fabs(GEnv.xTx[GEnv.ModelAtt[k]][jj])) > MaxElt) {
        MaxElt = Try;
      }
    }

    MinPivot = (GEnv.NModelAtt + 1) * MaxElt * 1E-12;

    max = j;
    Pivot = fabs(GEnv.A[j][j]);

    ForEach(k, j + 1, GEnv.NModelAtt) {
      if ((Try = fabs(GEnv.A[k][j])) > Pivot) {
        max = k;
        Pivot = Try;
      }
    }

    /*  Make diagonal element 1 if possible.  If cannot, note that
        matrix is singular and exclude this attribute  */

    if (Pivot < MinPivot) {
      GEnv.ZeroCoeff[GEnv.ModelAtt[j]] = Singular = true;
      Verbosity(3, printf("=== no pivot for %s (%g, max elt=%g)\n",
                          AttName[GEnv.ModelAtt[j]], Pivot, MaxElt))
    } else {
      if (max != j) {
        ExchangeRow(GEnv.B, max, j);
      }

      Pivot = GEnv.A[j][j]; /* actual pivot might be -ve */

      ForEach(k, j, GEnv.NModelAtt) { GEnv.A[j][k] /= Pivot; }
      GEnv.B[j] /= Pivot;

      ForEach(k, j + 1, GEnv.NModelAtt) { AddRow(GEnv.B, j, k, -GEnv.A[k][j]); }
    }
  }

  /*  If matrix is singular, try again without excluded attributes  */

  if (Singular) {
    FindActiveAtts();
    Solve(Model);
    return;
  }

  /*  Matrix is now triangular with 1 along diagonal  */

  for (j = GEnv.NModelAtt - 1; j >= 0; j--) {
    ForEach(k, j + 1, GEnv.NModelAtt) { GEnv.B[j] -= GEnv.A[j][k] * GEnv.B[k]; }
  }

  /*  Transfer values into Model  */

  ForEach(j, 1, MaxAtt) { Model[j] = 0; }

  ForEach(j, 0, GEnv.NModelAtt) { Model[GEnv.ModelAtt[j]] = GEnv.B[j]; }
}

/*************************************************************************/
/*                                                                       */
/* Construct list of active (non-excluded) attributes   */
/*                                                                       */
/*************************************************************************/

void FindActiveAtts(void)
/*   --------------  */
{
  Attribute Att;

  GEnv.NModelAtt = 0;
  ForEach(Att, 0, MaxAtt) {
    if (!GEnv.ZeroCoeff[Att])
      GEnv.ModelAtt[GEnv.NModelAtt++] = Att;
  }
  GEnv.NModelAtt--;
}

/*************************************************************************/
/*                                                                       */
/* Add Factor * row From to row To      */
/*                                                                       */
/*************************************************************************/

void AddRow(double *Model, short From, short To, double Factor)
/*   ------  */
{
  short col;
  double *ATo, *AFrom;

  ATo = &GEnv.A[To][0];
  AFrom = &GEnv.A[From][0];

  ForEach(col, 0, GEnv.NModelAtt) { ATo[col] += Factor * AFrom[col]; }

  Model[To] += Factor * Model[From];
}

/*************************************************************************/
/*                                                                       */
/* Exchange rows From and To      */
/*                                                                       */
/*************************************************************************/

void ExchangeRow(double *Model, short From, short To)
/*   -----------  */
{
  short col;
  double HoldVal;

  ForEach(col, 0, GEnv.NModelAtt) {
    HoldVal = GEnv.A[From][col];
    GEnv.A[From][col] = GEnv.A[To][col];
    GEnv.A[To][col] = HoldVal;
  }

  HoldVal = Model[From];
  Model[From] = Model[To];
  Model[To] = HoldVal;
}

/*************************************************************************/
/*                                                                       */
/* Count coefficients in Model      */
/*                                                                       */
/*************************************************************************/

int CountCoeffs(double *Model)
/*  -----------  */
{
  int Number = 1;
  Attribute Att;

  if (Model) {
    ForEach(Att, 1, MaxAtt) {
      if (fabs(Model[Att]) > 0) {
        Number++;
      }
    }
  }

  return Number;
}

/*************************************************************************/
/*                                                                       */
/* Simplify a model.       */
/* Drop coefficients one at a time, computing adjusted error;  */
/* then pick the model with lowest adjusted error.    */
/*                                                                       */
/*************************************************************************/

void SimplifyModel(DataRec *D, CaseNo Fp, CaseNo Lp, double *Model)
/*   -------------  */
{
  double ModErr, AdjModErr, BestAdjErr = 1E10, Contrib, LeastContrib, Wt,
                            Cases = 0;
  CaseNo i;
  Attribute Att, Drop;
  int a;
  Boolean Stable;

  ForEach(i, Fp, Lp) {
    Wt = CWeight(D[i]);
    Cases += Wt;
  }

  /*  Drop coefficients one at a time, selecting the coefficient that
      makes the least contribution to the model  */

  memcpy(GEnv.SaveZero, GEnv.ZeroCoeff, (MaxAtt + 1) * sizeof(Boolean));

  do {
    Verbosity(3,
              {
                fprintf(Of, "Model %.3f", Model[0]);
                ForEach(Att, 1, MaxAtt) {
                  if (GEnv.ZeroCoeff[Att]) {
                    fprintf(Of, " *");
                  } else {
                    fprintf(Of, " %.3f", Model[Att]);
                  }
                }
                fprintf(Of, "\n");
              })

        Stable = true;
    Drop = 0;
    ForEach(a, 1, GEnv.NModelAtt) {
      Att = GEnv.ModelAtt[a];
      Contrib = fabs(Model[Att] * GEnv.AvDev[Att]);

      if (!Drop || Contrib < LeastContrib) {
        Drop = Att;
        LeastContrib = Contrib;
      }

      if (Contrib > 1000 * GEnv.AvDev[0])
        Stable = false;
    }

    /*  Check whether current model is best so far  */

    if (Stable && Cases >= 2 * GEnv.NModelAtt) {
      ModErr = AverageErr(D, Fp, Lp, Model);
      AdjModErr = EstimateErr(ModErr, Cases, GEnv.NModelAtt);

      Verbosity(3, fprintf(Of, "Cases %d:%d  mod err=%.2f/%.2f%s\n", Fp, Lp,
                           ModErr, AdjModErr,
                           (AdjModErr <= BestAdjErr ? " **" : "")))

          if (AdjModErr <= BestAdjErr) {
        BestAdjErr = AdjModErr;
        memcpy(GEnv.BestModel, Model, (MaxAtt + 1) * sizeof(double));
      }
    }

    if (Drop) {
      Verbosity(3, fprintf(Of, "Drop %s  coeff=%.3f  mean=%.3f  |dev|=%.3f\n",
                           AttName[Drop], Model[Drop], GEnv.Mean[Drop],
                           GEnv.AvDev[Drop]))

          Model[Drop] = 0;
      GEnv.ZeroCoeff[Drop] = true;

      /*  Construct new model using remaining attributes  */

      FindActiveAtts();
      Solve(Model);
    }
  } while (Drop);

  memcpy(Model, GEnv.BestModel, (MaxAtt + 1) * sizeof(double));
  memcpy(GEnv.ZeroCoeff, GEnv.SaveZero, (MaxAtt + 1) * sizeof(Boolean));
}
