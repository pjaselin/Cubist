#*************************************************************************#
#*									 *#
#*		Makefile for the Cubist system				 *#
#*		------------------------------				 *#
#*									 *#
#*************************************************************************#

CC	= gcc -ffloat-store
OFLAGS = -O3
CFLAGS = -DVerbOpt -g -Wall -O0
LFLAGS = $(S)
SHELL  = /bin/csh


#	Definitions of file sets
#	New file order suggested by gprof
src =\
	global.c\
	xval.c\
	cubist.c\
	sort.c\
	construct.c\
	predict.c\
	stats.c\
	discr.c\
	rules.c\
	contin.c\
	formrules.c\
	formtree.c\
	getdata.c\
	getnames.c\
	implicitatt.c\
	instance.c\
	modelfiles.c\
	prunetree.c\
	regress.c\
	trees.c\
	update.c\
	utility.c

obj =\
	 global.o cubist.o construct.o\
	 formtree.o prunetree.o stats.o discr.o contin.o\
	 trees.o\
	 formrules.o rules.o\
	 instance.o\
	 predict.o\
	 regress.o\
	 xval.o\
	 getnames.o getdata.o implicitatt.o sort.o\
	 modelfiles.o\
	 update.o utility.o\


all:
	make cubist
	$(CC) $(LFLAGS) $(OFLAGS) -o summary summary.c -lm


# debug version (including verbosity option)

cubistdbg:\
	$(obj) defns.i extern.i text.i Makefile
	$(CC) $(CFLAGS) -o cubistdbg $(obj) -lm


# production version

cubist:\
	$(src) defns.i text.i Makefile
	cat defns.i $(src)\
		| egrep -v 'defns.i|extern.i' >cubistgt.c
	$(CC) $(LFLAGS) $(OFLAGS) -o cubist cubistgt.c -lm
	strip cubist
	rm cubistgt.c


$(obj):		Makefile defns.i extern.i text.i


.c.o:
	$(CC) $(CFLAGS) -c $<
