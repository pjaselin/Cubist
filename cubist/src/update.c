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
/*  Routines that provide information on progress   */
/*              ---------------------------------------------   */
/*                                                                       */
/*************************************************************************/

#include "defns.h"
#include "extern.h"

#include "redefine.h"
#include "transform.h"

int Stage = 0; /* Current stage number  */
FILE *Uf = 0;  /* File to which update info written  */

/*************************************************************************/
/*                                                                       */
/* There are twelve stages (see messages in Progress() below)  */
/* Record stage and open update file if necessary    */
/*                                                                       */
/*************************************************************************/

void NotifyStage(int S)
/*   -----------  */
{
  Stage = S;
  if (S == 1) {
    if (!(Uf = GetFile(".tmp", "w")))
      Error(0, "", E_ForWrite);
  }
}

/*************************************************************************/
/*                                                                       */
/* Print progress message.  This routine is called in two ways:  */
/*   *  negative Delta = measure of total effort required for stage */
/*   *  positive Delta = increment since last call    */
/*                                                                       */
/*************************************************************************/

void Progress(float Delta)
/*   --------  */
{
  static float Total, Current = 0;
  static int Twentieth, Percent = -6;
  int p;
  static char *Message[] = {"",
                            "Reading training data      ",
                            "Grouping training cases    ",
                            "Adding linear models       ",
                            "Simplifying groups         ",
                            "Forming rules              ",
                            "Preparing instance index   ",
                            "Setting number of neighbors",
                            "Assessing composite models ",
                            "Evaluating on training data",
                            "Reading test data          ",
                            "Evaluating on test data    ",
                            "Cleaning up                "},

              Tell[] = {0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0},

              *Unit[] = {"",
                         "",
                         "cases covered",
                         "models added",
                         "groups discarded",
                         "cases covered",
                         "",
                         "cases assessed",
                         "cases assessed",
                         "cases checked",
                         "",
                         "cases checked",
                         ""},

              *Done = ">>>>>>>>>>>>>>>>>>>>", *ToDo = "....................";

  if (Delta < 0) {
    Total = -Delta;
    Current = 0;
    Percent = -6;
  } else {
    Current += Delta;
  }

  if ((p = (100 * Current) / Total) == 100 || p >= Percent + 5) {
    Percent = p;
    Twentieth = p / 5;
    fprintf(Uf, "%s", Message[Stage]);
    if (Tell[Stage]) {
      fprintf(Uf, "  %s%s  (%d %s)", Done + (20 - Twentieth), ToDo + Twentieth,
              (int)(Current + 0.5), Unit[Stage]);
    }
    fprintf(Uf, "\n");
    fflush(Uf);
  }
}
