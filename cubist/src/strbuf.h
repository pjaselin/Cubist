#ifndef _STRBUF_H_
#define _STRBUF_H_

#include <stdarg.h>

typedef struct _STRBUF {
  char *buf;          // The buffer itself
  unsigned int i;     // Current position in buffer
  unsigned int n;     // Current size of the data in the buffer
  unsigned int len;   // Current length of buffer
  int open;           // File open flag
  int own;            // Should memory be deallocated?
} STRBUF;

extern STRBUF *strbuf_create_empty(unsigned int len);
extern STRBUF *strbuf_create_full(char *data, unsigned int len);
extern STRBUF *strbuf_copy(STRBUF *sb);
extern int strbuf_open(STRBUF *sb);
extern int strbuf_close(STRBUF *sb);
extern int strbuf_rewind(STRBUF *sb);
extern int strbuf_truncate(STRBUF *sb);
extern void strbuf_destroy(STRBUF *sb);
extern int strbuf_vprintf(STRBUF *sb, const char *format, va_list ap);
extern int strbuf_printf(STRBUF *sb, const char *format, ...);
extern int strbuf_puts(STRBUF *sb, const char *s);
extern int strbuf_putc(STRBUF *sb, int c);
extern int strbuf_write(STRBUF *sb, const char *data, unsigned int n);
extern char *strbuf_gets(STRBUF *sb, char *s, unsigned int n);
extern int strbuf_getc(STRBUF *sb);
extern char *strbuf_getall(STRBUF *sb);

#endif