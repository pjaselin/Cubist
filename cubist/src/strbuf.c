#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "strbuf.h"

#ifndef TRUE
#define TRUE 1
#endif

#ifndef FALSE
#define FALSE 0
#endif

#define EXTRA_EXTEND 8192

/* Declare all local functions */
static int extend(STRBUF *sb, unsigned int nlen);

/*
 * Create a STRBUF with the specified initial length.
 */
STRBUF *strbuf_create_empty(unsigned int len) {
  STRBUF *sb;

  /* Allocate memory for the STRBUF */
  sb = (STRBUF *)malloc(sizeof(STRBUF));
  if (sb == NULL)
    return NULL;

  /* Allocate memory for the buffer */
  sb->buf = (unsigned char *)malloc(len);
  if (sb->buf == NULL) {
    free(sb);
    return NULL;
  }

  /* Finish initializing the STRBUF */
  sb->i = 0;
  sb->n = 0;
  sb->len = len;
  sb->open = TRUE;
  sb->own = TRUE;

  /* Return a pointer to the STRBUF */
  return sb;
}

/*
 * Create a STRBUF from a buffer.  This can't be extended, because
 * it doesn't assume that the memory has been dynamically allocated.
 * The data buffer is neither reallocated or freed for any reason.
 */
STRBUF *strbuf_create_full(unsigned char *data, unsigned int len) {
  STRBUF *sb;

  /* Allocate memory for the STRBUF */
  sb = (STRBUF *)malloc(sizeof(STRBUF));
  if (sb == NULL)
    return NULL;

  /* Finish initializing the STRBUF */
  sb->buf = data;
  sb->i = 0;
  sb->n = len;
  sb->len = len;
  sb->open = FALSE;
  sb->own = FALSE;

  /* Return a pointer to the STRBUF */
  return sb;
}

STRBUF *strbuf_copy(STRBUF *sb) {
  STRBUF *nsb;

  /* Allocate memory for the STRBUF */
  nsb = (STRBUF *)malloc(sizeof(STRBUF));
  if (nsb == NULL)
    return NULL;

  /* Allocate memory for the buffer */
  nsb->buf = (unsigned char *)malloc(sb->len);
  if (nsb->buf == NULL) {
    free(nsb);
    return NULL;
  }

  /* Finish initializing the STRBUF */
  memcpy(nsb->buf, sb->buf, sb->n); /* Only copy n, not len */
  nsb->i = 0;
  nsb->n = sb->n;
  nsb->len = sb->len;
  nsb->open = FALSE;
  nsb->own = TRUE;

  /* Return a pointer to the STRBUF */
  return nsb;
}

int strbuf_open(STRBUF *sb) {
  sb->open = TRUE;

  return 0;
}

int strbuf_close(STRBUF *sb) {
  sb->open = FALSE;

  return 0;
}

/*
 * Reset the position to the beginning of the buffer.
 */
int strbuf_rewind(STRBUF *sb) {
  /* Set the current position to 0 */
  sb->i = 0;

  return 0;
}

/*
 * Reset the the data size to the current position.
 */
int strbuf_truncate(STRBUF *sb) {
  /* Set the current data size to the current position */
  sb->n = sb->i;

  assert(sb->n <= sb->len);

  return 0;
}

/*
 * Deallocate the STRBUF and the buffer (if we should).
 */
void strbuf_destroy(STRBUF *sb) {
  /* Deallocate the buffer if we own it */
  if (sb->own)
    free(sb->buf);

  /* Clear the STRBUF (not necessary) */
  sb->buf = NULL;
  sb->i = -1;
  sb->n = 0;
  sb->len = 0;

  /* Deallocate the STRBUF */
  free(sb);
}

/*
 * Write the specified amount of data to the STRBUF.
 */
int strbuf_write(STRBUF *sb, const unsigned char *data, unsigned int n) {
  unsigned int nlen = sb->i + n; /* Minimum length needed */

  /* If the new string won't fit, extend sb */
  if (nlen > sb->len)
    if (extend(sb, nlen + EXTRA_EXTEND) != 0)
      return -1;

  /* Copy the data into the buffer, and update the position and size */
  memcpy(sb->buf + sb->i, data, n);
  sb->i += n;
  if (sb->i > sb->n)
    sb->n = sb->i;

  assert(sb->n <= sb->len);

  return 0;
}

int strbuf_printf(STRBUF *sb, const unsigned char *format, ...) {
  va_list ap;
  int status;

  va_start(ap, format);
  status = strbuf_vprintf(sb, format, ap);
  va_end(ap);

  return status;
}

int strbuf_vprintf(STRBUF *sb, const unsigned char *format, va_list ap) {
  int s;
  unsigned int nlen;
  int size = sb->len - sb->i; /* Remaining space left */
  va_list ap2;
  va_list ap3;

  /* Copy ap to ap2 in case we need to call vsnprintf a second time */
  va_copy(ap2, ap);

  /*
   * Attempt to write to "sb".  The return value "s" is the number of
   * characters (not including the trailing '\0') which would have
   * been written to the string if enough space had been available.
   * That (may) tell us how much we need to extend "sb" by if the first
   * attempt fails.  On Windows, it returns -1, so we have to call
   * _vscprintf to determine the amount of memory that we need.
   */
  if ((s = vsnprintf(sb->buf + sb->i, size, format, ap)) >= size || s < 0) {
#ifdef WIN32
    if (s < 0) {
      /*
       * Copy ap2 to ap3, and then call _vscprintf to determine
       * the amount of memory that we need.
       */
      va_copy(ap3, ap2);
      s = _vscprintf(format, ap3);
      va_end(ap3);
    }
#endif
    /*
     * This is sort of an assertion, but it's possible
     * it could happen if _vscprintf failed, or on very
     * old versions of glibc.
     */
    if (s < 0) {
      va_end(ap2);
      return -1;
    }
    /*
     * We didn't have enough space, but now we know how
     * much we need, so extend the STRBUF and do it again.
     * We'll also ask for a bit extra to avoid calling
     * realloc quite so often.
     */
    nlen = sb->n + s + 1; /* Minimum length needed */

    if (extend(sb, nlen + EXTRA_EXTEND) != 0) {
      va_end(ap2);
      return -1;
    }

    size = sb->len - sb->i; /* Recompute remaining space left */
    s = vsnprintf(sb->buf + sb->i, size, format, ap2);
    if (s >= size || s < 0) {
      va_end(ap2);
      return -1;
    }
  }

  /* This corresponds to the va_copy */
  va_end(ap2);

  /*
   * Bump the STRBUF's position by s, since
   * s doesn't include the trailing '\0'
   */
  sb->i += s;
  if (sb->i > sb->n)
    sb->n = sb->i;

  assert(sb->n <= sb->len);

  return 0;
}

/*
 * Write a null-terminated string to the STRBUF.
 */
int strbuf_puts(STRBUF *sb, const unsigned char *s) {
  return strbuf_write(sb, s, strlen(s));
}

/*
 * Write a character to the STRBUF.
 */
int strbuf_putc(STRBUF *sb, int c) {
  unsigned int nlen = sb->i + 1; /* Minimum length needed */

  /* If the new character won't fit, extend sb */
  if (nlen > sb->len)
    if (extend(sb, nlen + EXTRA_EXTEND) != 0)
      return -1;

  /* Put the character into the buffer, and update the position and size */
  sb->buf[sb->i++] = (unsigned char)c;
  if (sb->i > sb->n)
    sb->n = sb->i;

  assert(sb->n <= sb->len);

  return 0;
}

/*
 * Read a string from the STRBUF.
 */
unsigned char *strbuf_gets(STRBUF *sb, unsigned char *s, unsigned int n) {
  int c = -1;
  int i, j;

  for (i = 0, j = sb->i; i < n - 1 && j < sb->n && c != '\n'; i++, j++) {
    /* XXX Does this need to be cast to a char? */
    s[i] = sb->buf[j];
    c = sb->buf[j];
  }

  /* XXX What if n is 0?  Do we return NULL? */
  if (i == 0) {
    return NULL;
  }

  /* Null terminate the user's string and update position if success */
  s[i] = '\0';
  sb->i = j;

  return s;
}

/*
 * Read a character from the STRBUF.
 */
int strbuf_getc(STRBUF *sb) {
  int c = (sb->i < sb->n) ? sb->buf[sb->i++] : EOF;

  return c;
}

/*
 * Return the entire buffer.
 * Be careful, because it's not null-terminated!
 */
unsigned char *strbuf_getall(STRBUF *sb) {
  /* Make sure there is enough memory to null-terminate the data */
  if (sb->n >= sb->len) {
    /* sb->n should never actually be larger than sb->len */
    assert(sb->n == sb->len);
    if (extend(sb, sb->n + EXTRA_EXTEND) != 0)
      return NULL;
  }

  /*
   * Write an EOS immediately after the data.  This allows the caller
   * to treat the data as a standard null-terminated string.
   */
  sb->buf[sb->n] = '\0';

  return sb->buf;
}

/*
 * Increase the allocated size of the buffer to the specified size.
 */
static int extend(STRBUF *sb, unsigned int nlen) {
  unsigned char *buf;

  /* Do nothing if nlen isn't larger than the current size */
  if (nlen <= sb->len)
    return -1; /* Not sure if this should be called an error or not */

  /* Return an error if we don't own the buffer */
  if (!sb->own)
    return -1;

  /* Try to reallocate the buffer */
  buf = (unsigned char *)realloc(sb->buf, nlen);
  if (buf == NULL)
    return -1; /* Note that sb is untouched */

  /* Success, so update the STRBUF */
  sb->buf = buf;
  sb->len = nlen;

  return 0;
}
