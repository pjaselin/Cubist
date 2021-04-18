#ifndef _RULEBASEDMODELS_H_
#define _RULEBASEDMODELS_H_

extern void initglobals(void);
extern void setglobals(int unbiased, char *composite, int neighbors,
                       int committees, double sample, int seed, int rules,
                       double extrapolation);
extern void setOf(void);
extern char *closeOf(void);

#endif

#define JMP_OFFSET 100
extern jmp_buf rbm_buf;
