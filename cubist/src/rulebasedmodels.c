#include <setjmp.h>

#include "defns.h"
#include "extern.h"
#include "redefine.h"
#include "rulebasedmodels.h"
#include "strbuf.h"

/* Global variables defined in update.d */
extern int Stage;
extern FILE *Uf;

/* Used to implement rbm_exit */
jmp_buf rbm_buf;

/* Don't want to include R.h, which has conflicts with cubist headers */
// extern void Rprintf(const char *, ...);

/*
 * Reset all global variables to their initial value
 */
void initglobals(void)
/*   ---------- */
{
  /*************************************************************************/
  /*                                                                       */
  /*              General data for Cubist                                  */
  /*              -----------------------                                  */
  /*                                                                       */
  /* These variables are all defined in global.c.  Many aren't explicitly  */
  /* initialized there, but are here, just in case.                        */
  /*                                                                       */
  /*************************************************************************/

  ClassAtt = 0;
  LabelAtt = 0;
  CWtAtt = 0;

  IgnoredVals = 0;
  IValsSize = 0;
  IValsOffset = 0;

  MaxAtt = 0;
  MaxDiscrVal = 3;
  Precision = 0;
  MaxLabel = 0;
  LineNo = 0;
  ErrMsgs = 0;
  AttExIn = 0;
  TSBase = 0;

  MaxCase = -1;

  Case = Nil;

  SaveCase = Nil;
  Blocked = Nil;
  SaveMaxCase = 0;

  MaxAttVal = Nil;
  Modal = Nil;

  SpecialStatus = Nil;

  AttDef = Nil;
  AttDefUses = Nil;

  AttName = Nil;
  AttValName = Nil;

  Of = 0;
  FileStem = "undefined";

  AttMean = Nil;
  AttSD = Nil;
  AttMaxVal = Nil;
  AttMinVal = Nil;
  AttPref = Nil;
  Ceiling = 0.0;
  Floor = 0.0;
  AvCWt = 0.0;

  ErrReduction = 1;

  AttUnit = Nil;

  AttPrec = Nil;

  Instance = Nil;
  Ref[0] = Nil;
  Ref[1] = Nil;
  MaxInstance = -1;
  KDTree = Nil;

  RSPredVal = Nil;

  /*************************************************************************/
  /*                                                                       */
  /*        Global data for Cubist used for building model trees           */
  /*        ----------------------------------------------------           */
  /*                                                                       */
  /*************************************************************************/


  TempMT = Nil;

  SRec = Nil;

  GlobalMean = 0.0;
  GlobalSD = 0.0;
  GlobalErr = 0.0;

  Fn[0] = '\0';

  Mf = 0;
  Pf = 0;

  /*************************************************************************/
  /*                                                                       */
  /*      Global data for constructing and applying rules                  */
  /*      -----------------------------------------------                  */
  /*                                                                       */
  /*************************************************************************/

  Rule = Nil;
  NRules = 0;
  RuleSpace = 0;

  Cttee = Nil;

  /*************************************************************************/
  /*                                                                       */
  /*              Global parameters for Cubist                             */
  /*              ----------------------------                             */
  /*                                                                       */
  /*************************************************************************/

  VERBOSITY = 0;
  FOLDS = 10;
  NN = 0;
  MEMBERS = 1;

  MAXD = 0.0;

  XVAL = 0;
  CHOOSEMODE = 0;
  USEINSTANCES = 0;
  UNBIASED = 0;

  SAMPLE = 0.0;
  KRInit = 0;
  LOCK = false;

  MINITEMS = 0;
  MAXRULES = 100;

  EXTRAP = 0.1;

  /**********************************************/
  /*                                            */
  /* Reinitialize variables defined in update.c */
  /*                                            */
  /**********************************************/

  Stage = 0;
  Uf = 0;
}

/*
 * Set global variables in preparation for creating a model
 */
void setglobals(int unbiased, char *composite, int neighbors, int committees,
                double sample, int seed, int rules, double extrapolation) {
  /* XXX What about setting FOLDS? */

  UNBIASED = unbiased != 0 ? true : false;

  if (strcmp(composite, "yes") == 0) {
    USEINSTANCES = true;
    CHOOSEMODE = false;
  } else if (strcmp(composite, "auto") == 0) {
    USEINSTANCES = true;
    CHOOSEMODE = true;
  } else {
    USEINSTANCES = neighbors > 0;
    CHOOSEMODE = false;
  }

  NN = neighbors;
  MEMBERS = committees;
  SAMPLE = sample;
  KRInit = seed;
  MAXRULES = rules;
  EXTRAP = extrapolation;
}

void setOf() {
  // XXX Experimental
  Of = rbm_fopen("rulebasedmodels.stdout", "w");
}

char *closeOf() {
  if (Of) {
    rbm_fclose(Of);
    return strbuf_getall((STRBUF *)Of);
  } else {
    return "";
  }
}

/*
 * The jmp_buf needs to be initialized before calling this.
 * Also, this must be called further down the stack from the
 * code that called setjmp to initialize rbm_buf.
 * That's why we can't have a function that initialize the
 * jmp_buf, but must use a macro instead.
 */
void rbm_exit(int status) {
  /* This doesn't return */
  longjmp(rbm_buf, status + JMP_OFFSET);
}
