EXTENSION    = saio
EXTVERSION   = $(shell grep default_version $(EXTENSION).control | \
               sed -e "s/default_version[[:space:]]*=[[:space:]]*'\([^']*\)'/\1/")

PG_CPPFLAGS  = -std=c99 -Wall
SHLIB_LINK   = 
DOCS         = $(wildcard doc/*.md)
TESTS        = $(wildcard test/sql/*.sql)
REGRESS      = $(patsubst test/sql/%.sql,%,$(TESTS))
REGRESS_OPTS = --inputdir=test
PG_CONFIG    = pg_config


EXTRA_CLEAN = src/saio_probes.h

MODULE_big = saio
OBJS = src/saio_main.o src/saio_util.o src/saio_trees.o \
	src/saio_recalc.o src/saio.o

# make sure
all: all-lib


coverage:
	lcov -d . -c -o lcov.info
	genhtml --show-details --legend --output-directory=coverage --title=PostgreSQL --num-spaces=4 --prefix=./src/ `find . -name lcov.info -print`


# check for DTrace support
ifeq (,$(findstring --enable-dtrace,$(shell $(PG_CONFIG) --configure)))
enable_dtrace = no
else
enable_dtrace = yes
endif

ifeq ($(enable_dtrace), yes)
OBJS += src/saio_probes.o
endif

src/saio.o: src/saio_probes.h

src/saio_probes.o: src/saio_probes.d
	$(DTRACE) -C -G -s $< -o $@

ifeq ($(enable_dtrace), no)
src/saio_probes.h: src/Gen_dummy_probes.sed
endif

src/saio_probes.h: src/saio_probes.d
ifeq ($(enable_dtrace), yes)
	$(DTRACE) -C -h -s $< -o $@.tmp
	sed -e 's/SAIO_/TRACE_SAIO_/g' $@.tmp >$@
	rm $@.tmp
else
	sed -f src/Gen_dummy_probes.sed $< >$@
endif


OS := $(shell uname)
ifeq ($(OS), Linux)
SHLIB_LINK += -Wl,-Bsymbolic
endif

PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
