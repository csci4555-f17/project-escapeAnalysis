CC=gcc
CFLAGS=-m32 -O2

SRC = $(wildcard *.c)
OBJ = $(SRC:.c=.o)

LIBPYYRUNTIME = libpyyruntime.a

$(LIBPYYRUNTIME): $(OBJ)
	$(AR) -rcs $@ $^

.PHONY: clean
clean:
	rm -f $(OBJ) $(LIBPYYRUNTIME)
