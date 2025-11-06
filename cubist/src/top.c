#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <setjmp.h>
#include "redefine.h"
#include "rulebasedmodels.h"
#include "strbuf.h"

extern void cubistmain(void);
extern void samplemain(double *outputv);
extern void FreeCases(void);

static void cubist(char **namesv, char **datav, int *unbiased,
                   char **compositev, int *neighbors, int *committees,
                   double *sample, int *seed, int *rules, double *extrapolation,
                   int *cv, char **modelv, char **outputv) {
  int val; /* Used by setjmp/longjmp for implementing rbm_exit */

  // Initialize the globals to the values that the cubist
  // program would have at the start of execution
  initglobals();

  // Set globals based on the arguments.  This is analogous
  // to parsing the command line in the cubist program.
  setglobals(*unbiased, *compositev, *neighbors, *committees, *sample, *seed,
             *rules, *extrapolation, *cv);
  
  // Handles the strbufv data structure
  rbm_removeall();

  // Deallocates memory allocated by NewCase.
  // Not necessary since it's also called at the end of this function,
  // but it doesn't hurt, and I'm feeling paranoid.
  FreeCases();

  // XXX Should this be controlled via an option?
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
    cubistmain();
    
    // Get the contents of the the model file if not using cross-validation
    if (*cv == 0){
      char *modelString = strbuf_getall(rbm_lookup("undefined.model"));
      char *model = PyMem_Calloc(strlen(modelString) + 1, 1);
      strcpy(model, modelString);

      // I think the previous value of *modelv will be garbage collected
      *modelv = model;
    }
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

  // Initialize the globals
  initglobals();

  // Handles the strbufv data structure
  rbm_removeall();

  // XXX Should this be controlled via an option?
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
    samplemain(predv);

  } //else {
    // printf("prediction code called exit with value %d\n", val - JMP_OFFSET);
  // }

  // Close file object "Of", and return its contents via argument outputv
  char *outputString = closeOf();
  char *output = PyMem_Calloc(strlen(outputString) + 1, 1);
  strcpy(output, outputString);
  *outputv = output;

  // We reinitialize the globals on exit out of general paranoia
  initglobals();
}
