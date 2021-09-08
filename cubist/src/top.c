#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <setjmp.h>
#include "redefine.h"
#include "rulebasedmodels.h"
#include "strbuf.h"

extern void cubistmain();
extern void samplemain(double *outputv);
extern void FreeCases(void);

static void cubist(char **namesv, char **datav, int *unbiased,
                   char **compositev, int *neighbors, int *committees,
                   double *sample, int *seed, int *rules, double *extrapolation,
                   char **modelv, char **outputv) {
  int val; /* Used by setjmp/longjmp for implementing rbm_exit */
  
  // Announce ourselves for testing
  // printf("cubist called\n");

  // Initialize the globals to the values that the cubist
  // program would have at the start of execution
  initglobals();

  // Set globals based on the arguments.  This is analogous
  // to parsing the command line in the cubist program.
  setglobals(*unbiased, *compositev, *neighbors, *committees, *sample, *seed,
             *rules, *extrapolation);

  // Handles the strbufv data structure
  rbm_removeall();

  // Deallocates memory allocated by NewCase.
  // Not necessary since it's also called at the end of this function,
  // but it doesn't hurt, and I'm feeling paranoid.
  FreeCases();

  // XXX Should this be controlled via an option?
  // printf("Calling setOf\n");
  setOf();

  // Create a strbuf using *namesv as the buffer.
  // Note that this is a readonly strbuf since we can't
  // extend *namesv.
  STRBUF *sb_names = strbuf_create_full(*namesv, strlen(*namesv));

  // Register this strbuf using the name "undefined.names"
  rbm_register(sb_names, "undefined.names", 1);

  // Create a strbuf using *datav and register it as "undefined.data"
  STRBUF *sb_datav = strbuf_create_full(*datav, strlen(*datav));
  // XXX why is sb_datav copied? what that part of my debugging?
  rbm_register(strbuf_copy(sb_datav), "undefined.data", 1);

  /*
   * We need to initialize rbm_buf before calling any code that
   * might call exit/rbm_exit.
   */
  if ((val = setjmp(rbm_buf)) == 0) {
    // Real work is done here
    // printf("Calling cubistmain\n");
    cubistmain();

    // printf("cubistmain finished\n");

    // Get the contents of the the model file
    char *modelString = strbuf_getall(rbm_lookup("undefined.model"));
    char *model = PyMem_Calloc(strlen(modelString) + 1, 1);
    strcpy(model, modelString);
    

    // I think the previous value of *modelv will be garbage collected
    *modelv = model;
  } else {
    printf("cubist code called exit with value %d\n", val - JMP_OFFSET);
//    Rprintf("cubist code called exit with value %d\n", val - JMP_OFFSET);
  }

  // Close file object "Of", and return its contents via argument outputv
  char *outputString = closeOf();
  char *output = PyMem_Calloc(strlen(outputString) + 1, 1);
  strcpy(output, outputString);
  *outputv = output;

  // Deallocates memory allocated by NewCase
  FreeCases();

  // We reinitialize the globals on exit out of general paranoia
  initglobals();
}

static void predictions(char **casev, char **namesv, char **datav,
                        char **modelv, double *predv, char **outputv) {
  int val; /* Used by setjmp/longjmp for implementing rbm_exit */

  // Announce ourselves for testing
  // Rprintf("predictions called\n");

  // Initialize the globals
  initglobals();

  // Handles the strbufv data structure
  rbm_removeall();

  // XXX Should this be controlled via an option?
  // Rprintf("Calling setOf\n");
  setOf();

  STRBUF *sb_cases = strbuf_create_full(*casev, strlen(*casev));
  rbm_register(sb_cases, "undefined.cases", 1);

  STRBUF *sb_names = strbuf_create_full(*namesv, strlen(*namesv));
  rbm_register(sb_names, "undefined.names", 1);

  STRBUF *sb_datav = strbuf_create_full(*datav, strlen(*datav));
  // /* XXX why is sb_datav copied? */
  rbm_register(strbuf_copy(sb_datav), "undefined.data", 1);

  STRBUF *sb_modelv = strbuf_create_full(*modelv, strlen(*modelv));
  /* XXX should sb_modelv be copied? */
  rbm_register(sb_modelv, "undefined.model", 1);

  /*
   * We need to initialize rbm_buf before calling any code that
   * might call exit/rbm_exit.
   */
  if ((val = setjmp(rbm_buf)) == 0) {
    // Real work is done here
    // Rprintf("Calling samplemain\n");
    samplemain(predv);

    // Rprintf("samplemain finished\n");
  } else {
    // Rprintf("sample code called exit with value %d\n", val - JMP_OFFSET);
  }

  // Close file object "Of", and return its contents via argument outputv
  char *outputString = closeOf();
  char *output = PyMem_Calloc(strlen(outputString) + 1, 1);
  strcpy(output, outputString);
  *outputv = output;

  // We reinitialize the globals on exit out of general paranoia
  initglobals();
}

// Declare the type of each of the arguments to the cubist function
//static R_NativePrimitiveArgType cubist_t[] = {
//    STRSXP,  // namesv
//    STRSXP,  // datav
//    LGLSXP,  // unbiased
//    STRSXP,  // compositev
//    INTSXP,  // neighbors
//    INTSXP,  // committees
//    REALSXP, // sample
//    INTSXP,  // seed
//    INTSXP,  // rules
//    REALSXP, // extrapolation
//    STRSXP,  // modelv
//    STRSXP   // outputv
//};

// Declare the type of each of the arguments to the cubist function
//static R_NativePrimitiveArgType predictions_t[] = {
//    STRSXP,  // casev
//    STRSXP,  // namesv
//    STRSXP,  // datav
//    STRSXP,  // modelv
//    REALSXP, // predv
//    STRSXP   // outputv
//};

// Declare the cubist function
//static const R_CMethodDef cEntries[] = {
//    {"cubist", (DL_FUNC)&cubist, 12, cubist_t},
//    {"predictions", (DL_FUNC)&predictions, 6, predictions_t},
//    {NULL, NULL, 0}};

// Initialization function for this shared object
//void R_init_Cubist(DllInfo *dll) {
//  // Announce ourselves for testing
//  // Rprintf("R_init_Cubist called\n");
//
//  // Register the functions "cubist" and "predictions"
//  R_registerRoutines(dll, cEntries, NULL, NULL, NULL);
//
//  // This should help prevent people from accidentally accessing
//  // any of our global variables, or any functions that are not
//  // intended to be called from R.  Only the functions "cubist"
//  // and predictions  can be accessed, since they're the only ones
//  // we registered.
//  R_useDynamicSymbols(dll, FALSE);
//}
