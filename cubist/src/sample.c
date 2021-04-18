#include "defns.h"
#include "extern.h"

/*************************************************************************/
/*                                                                       */
/* Main                                                             */
/*                                                                       */
/*************************************************************************/

#ifdef MAIN_PROGRAM
#define MAIN main
#else
#define MAIN Ymain
#endif

int MAIN(int Argc, char *Argv[])
/*  ----------  */
{
  RRuleSet *CubistModel;
  double pval;
  FILE *F;
  int o;
  extern String OptArg, Option;
  CaseNo i;

  /*  Process options  */

  while ((o = ProcessOption(Argc, Argv, "f+"))) {
    switch (o) {
    case 'f':
      FileStem = OptArg;
      break;
    case '?':
      break; /* printf("    **Unrecognised option %s\n", Option); */
             /* The above was commented out to pass R CMD check: "Compiled code
                should [...]  write to stdout/stderr instead of to the
                console" */

      /* TODO: change this exit to rbm_exit to avoid R CMD check
         errors */
      /*     exit(1); */
    }
  }

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

  /* commented out to pass R CMD check: "Compiled code should
         [...]  write to stdout/stderr instead of to the console" */
  /* printf("predicted values:\n"); */

  ForEach(i, 0, MaxCase) {
    pval = PredVal(Case[i]);
    /* commented out to pass R CMD check: "Compiled code should
       [...]  write to stdout/stderr instead of to the console" */
    /* printf("%f\n", pval); */
  }

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
