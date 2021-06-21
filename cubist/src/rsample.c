#include "defns.h"
#include "extern.h"

/*************************************************************************/
/*                                                                       */
/* Main                                                             */
/*                                                                       */
/*************************************************************************/

int samplemain(double *outputv)
/*  ----------  */
{
  RRuleSet *CubistModel;
  FILE *F;
  CaseNo i;

  /*  Read information on attribute names and values  */

  if (!(F = GetFile(".names", "r")))
    Error(0, Fn, "");
  GetNames(F); /* GetNames closes the file */

  /*
   * Calling NotifyStage with READDATA initializes the Uf variable.
   * Otherwise, calling InitialiseInstances will seg fault.
   */
  NotifyStage(READDATA);
  Progress(-1.0);

  /*  Read the model file that defines the ruleset and sets values
      for various global variables such as USEINSTANCES  */

  CubistModel = GetCommittee(".model");

  if (USEINSTANCES) {
    if (!(F = GetFile(".data", "r")))
      Error(0, Fn, "");
    GetData(F, true, false); /* GetData closes the file */

    /* Prepare the file of instances and the kd-tree index  */
    InitialiseInstances(CubistModel);

    /* Reorder instances to improve caching  */
    CopyInstances();

    /* Free memory allocated by GetData */
    FreeData(Case);
    Case = Nil;
  }

  if (!(F = GetFile(".cases", "r")))
    Error(0, Fn, "");

  /* Not training, but allow unknown target */
  GetData(F, false, true); /* GetData closes the file */

  FindPredictedValues(CubistModel, 0, MaxCase);

  ForEach(i, 0, MaxCase) { outputv[i] = PredVal(Case[i]); }

  /* Free memory allocated by GetCommittee */
  FreeCttee(CubistModel);
  CubistModel = Nil;

  /* Free memory allocated by GetData */
  FreeData(Case);
  Case = Nil;

  if (USEINSTANCES) {
    /* Free memory allocated by InitialiseInstances and CopyInstances */
    FreeInstances();
  }

  /* Free memory allocated by GetNames */
  FreeNamesData();

  return 0;
}
