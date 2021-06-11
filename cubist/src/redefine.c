/*
 * This file contains replacements for file and directory
 * operations from the standard I/O library (stdio).
 * Basically, it replaces file operations with string buffer
 * operations (using functions declared in strbuf.h),
 * and it replaces directory operations with a single
 * hash table/associative array (using functions declared in
 * hash.h).
 *
 * Note that currently the purpose of this is to work
 * well enough for use in the Cubist package.
 * Thus, it is not completely general, since that would
 * make the code far more complex than it already is.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "hash.h"
#include "redefine.h"
#include "strbuf.h"

/* Don't want to include R.h which has conflicts */
// extern void Rprintf(const char *, ...);

/*
 * Not sure what value to use, but it will be automatically increased
 * if necessary, so the initial value is not critical, but a larger value
 * will help avoid a realloc with each printf. Use powers of 2
 * to hopefully make memory allocation more smooth
 */
#define STRBUF_LEN 8192

#define HASH_LEN 128

/*
 * This is used to save the contents of files that have been
 * created and written.
 */
static void *strbufv;

/*
 * XXX Is this called anywhere in Cubist?  It looks like it's
 * XXX been made obsolete by rbm_removeall.
 */
int rbm_init() {
  if (strbufv == NULL) {
    strbufv = ht_new(HASH_LEN);
  }
  return strbufv == NULL ? -1 : 0;
}

/* This is similar to rbm_fopen */
int rbm_register(STRBUF *sb, const char *filename, int force) {
  // Rprintf("rbm_register: registering file: %s\n", filename);

  if (ht_lookup(strbufv, filename) != NULL) {
    if (force) {
      printf("rbm_register: warning: file already registered: %s\n", filename);
    } else {
      printf("rbm_register: error: file already registered: %s\n", filename);
      return -1;
    }
  }

  /* XXX Should I provide an "isopen" function for STRBUF? */
  if (sb->open) {
    printf("rbm_register: error: cannot register an open file: %s\n",
            filename);
    return -1;
  }

  ht_setvoid(strbufv, filename, sb);

  return 0;
}

/* This is similar to rbm_remove, but doesn't destroy the STRBUF */
int rbm_deregister(const char *filename) {
  // Rprintf("rbm_deregister: deregistering file: %s\n", filename);

  if (ht_delete(strbufv, filename) != 0) {
    printf("rbm_deregister: error: file not registered: %s\n", filename);
    return -1;
  }

  return 0;
}

STRBUF *rbm_lookup(const char *filename) {
  STRBUF *sb = ht_getvoid(strbufv, filename, NULL, NULL);
  if (sb == NULL) {
    printf("rbm_lookup: error: no file registered: %s\n", filename);
    return NULL;
  }

  return sb;
}

FILE *rbm_fopen(const char *filename, const char *mode) {
  STRBUF *sb;
  STRBUF *id = ht_getvoid(strbufv, filename, NULL, NULL);

  /* Only the "w" mode is currently supported */
  if (strcmp(mode, "w") == 0) {
    // Rprintf("rbm_fopen: opening file to write: %s\n", filename);
    sb = strbuf_create_empty(STRBUF_LEN);
    if (id != NULL) {
      printf("rbm_fopen: warning: destroying previous STRBUF: %s\n", filename);
      strbuf_destroy(id);
    }
    ht_setvoid(strbufv, filename, sb);
  } else {
    // Rprintf("rbm_fopen: opening file to read: %s\n", filename);
    sb = id;
    if (sb != NULL) {
      if (sb->open) {
        printf("rbm_fopen: error: file already open: %s\n", filename);
        sb = NULL; // XXX Is this right?
      } else {
        strbuf_open(sb);
        strbuf_rewind(sb);
      }
    } else {
      // Rprintf("rbm_fopen: no such file: %s\n", filename);
      sb = NULL;
    }
  }

  return (FILE *)sb;
}

int rbm_fclose(FILE *stream) { return strbuf_close((STRBUF *)stream); }

int rbm_fflush(FILE *stream) {
  /* Nothing to do */
  return 0;
}

void rbm_rewind(FILE *stream) { strbuf_rewind((STRBUF *)stream); }

int rbm_fgetc(FILE *stream) { return strbuf_getc((STRBUF *)stream); }

int rbm_getc(FILE *stream) { return strbuf_getc((STRBUF *)stream); }

char *rbm_fgets(char *s, int n, FILE *stream) {
  return strbuf_gets((STRBUF *)stream, s, n);
}

int rbm_fprintf(FILE *stream, const char *format, ...) {
  va_list ap;
  int status;

  va_start(ap, format);
  status = strbuf_vprintf((STRBUF *)stream, format, ap);
  va_end(ap);

  return status;
}

int rbm_fputc(int c, FILE *stream) { return strbuf_putc((STRBUF *)stream, c); }

int rbm_putc(int c, FILE *stream) { return strbuf_putc((STRBUF *)stream, c); }

int rbm_fputs(const char *s, FILE *stream) {
  return strbuf_puts((STRBUF *)stream, s);
}

size_t rbm_fwrite(const void *ptr, size_t size, size_t nitems, FILE *stream) {
  return strbuf_write((STRBUF *)stream, ptr, nitems * size);
}

int rbm_remove(const char *path) {
  STRBUF *sb = rbm_lookup(path);

  if (sb == NULL) {
    return -1;
  }

  rbm_deregister(path);
  strbuf_destroy(sb);

  return 0;
}

/*
 * This is called at the beginning of a cubist run to clear out
 * all "files" generated on the previous run and to prepare it
 * for the next run.
 */
void rbm_removeall() {
  /* Check if there actually is anything to remove */
  if (strbufv != NULL) {
    /*
     * Destroy all STRBUF's in the hash table.
     * Note that this loop leaves the hash table full of
     * pointers to deallocated STRBUF's until ht_destroy
     * is called below.
     */
    ht_reset(strbufv); /* just in case */
    while (1) {
      void *e = ht_next(strbufv);
      if (e == NULL)
        break;
      strbuf_destroy((STRBUF *)ht_value(e));
    }

    /* Destroy the hash table itself */
    ht_destroy(strbufv);
  }

  /* Create/recreate the hash table for subsequent use */
  strbufv = ht_new(HASH_LEN);
}
