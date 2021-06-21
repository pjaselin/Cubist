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
/* Main routine, Cubist       */
/* --------------------       */
/*                                                                       */
/*************************************************************************/

#include "defns.h"
#include "extern.h"

#include <time.h>

#include "redefine.h"
#include "transform.h"

int cubistmain()
/*  ----------  */
{
  double StartTime, SumCWt = 0;
  FILE *F;
  CaseNo SaveMaxCase, i, NCWt = 0;
  Attribute Att;

  KRInit = time(0) & 07777;
  StartTime = ExecTime();
  PrintHeader("");

  /*  Get information on training data  */

  if (!(F = GetFile(".names", "r")))
    Error(NOFILE, "", "");
  GetNames(F);

  fprintf(Of, T_TargetAtt, AttName[ClassAtt]);

  NotifyStage(READDATA);
  Progress(-1.0);

  if (!(F = GetFile(".data", "r")))
    Error(NOFILE, "", "");
  GetData(F, true, false);
  fprintf(Of, TX_ReadData(MaxCase + 1, MaxAtt, FileStem));

  if (XVAL && (F = GetFile(".test", "r"))) {
    SaveMaxCase = MaxCase;
    GetData(F, false, false);
    fprintf(Of, TX_ReadTest(MaxCase - SaveMaxCase, FileStem));
  }

  /*  Check whether case weight attribute appears.  If it does,
      normalize values to average 1, and replace N/A values and
      values <= 0 with average value 1  */

  if (CWtAtt) {
    fprintf(Of, T_CWtAtt);

    /*  Find average case weight value  */

    ForEach(i, 0, MaxCase) {
      if (!NotApplic(Case[i], CWtAtt) && CVal(Case[i], CWtAtt) > 0) {
        SumCWt += CVal(Case[i], CWtAtt);
        NCWt += 1;
      }
    }

    AvCWt = (NCWt > 0 ? SumCWt / NCWt : 1);

    ForEach(i, 0, MaxCase) {
      if (!NotApplic(Case[i], CWtAtt) && CVal(Case[i], CWtAtt) > 0) {
        CVal(Case[i], CWtAtt) /= AvCWt;
      } else {
        CVal(Case[i], CWtAtt) = 1;
      }
    }
  } else {
    AvCWt = 1;
  }

  /*  Note any attribute exclusions/inclusions  */

  if (AttExIn) {
    fprintf(Of, "%s", (AttExIn == -1 ? T_AttributesOut : T_AttributesIn));

    ForEach(Att, 1, MaxAtt) {
      if ((StatBit(Att, SKIP) > 0) == (AttExIn == -1)) {
        fprintf(Of, "    %s\n", AttName[Att]);
      }
    }
  }

  /*  Build and evaluate cubist model  */

  InitialiseEnvData();

  if (XVAL) {
    CrossVal();
  } else {
    SingleCttee();
  }

#ifdef VerbOpt
  Cleanup();
#endif

  fprintf(Of, T_Time, ExecTime() - StartTime);

  return 0;
}
