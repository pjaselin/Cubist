#ifdef putc
#undef putc
#endif
#ifdef getc
#undef getc
#endif

#define getc(X) rbm_getc(X)
#define putc(X, Y) rbm_putc(X, Y)

#define fopen(X, Y) rbm_fopen(X, Y)
#define fclose(X) rbm_fclose(X)
#define fflush(X) rbm_fflush(X)
#define rewind(X) rbm_rewind(X)
#define fgetc(X) rbm_fgetc(X)
#define fgets(X, Y, Z) rbm_fgets(X, Y, Z)
#define fprintf rbm_fprintf
#define fputc(X, Y) rbm_fputc(X, Y)
#define fputs(X, Y) rbm_fputs(X, Y)
#define fwrite(X, Y, Z, A) rbm_fwrite(X, Y, Z, A)
#define remove(X) rbm_remove(X)

#define exit(X) rbm_exit(X)

// #define printf Rprintf
#define puts(X) printf("%s", X)
