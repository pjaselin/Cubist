#ifndef _REDEFINE_H_
#define _REDEFINE_H_

#include <setjmp.h>
#include <stdio.h>

#include "strbuf.h"

extern int rbm_init();
extern int rbm_register(STRBUF *sb, const char *filename, int force);
extern int rbm_deregister(const char *filename);
extern STRBUF *rbm_lookup(const char *filename);
extern FILE *rbm_fopen(const char *filename, const char *mode);
extern int rbm_fclose(FILE *stream);
extern int rbm_fflush(FILE *stream);
extern void rbm_rewind(FILE *stream);
extern int rbm_fgetc(FILE *stream);
extern int rbm_getc(FILE *stream);
extern char *rbm_fgets(char *s, int n, FILE *stream);
extern int rbm_fprintf(FILE *stream, const char *format, ...);
extern int rbm_fputc(int c, FILE *stream);
extern int rbm_putc(int c, FILE *stream);
extern int rbm_fputs(const char *s, FILE *stream);
extern size_t rbm_fwrite(const void *ptr, size_t size, size_t nitems,
                         FILE *stream);
extern int rbm_remove(const char *fname);
extern void rbm_removeall();
extern void rbm_exit(int status);

#endif
