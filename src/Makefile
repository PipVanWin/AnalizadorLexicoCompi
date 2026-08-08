# Makefile - Analizador Lexico

CC = gcc
FLEX = flex
CFLAGS = -Wall -O2

all: analizador

lex.yy.c: lexer.l
	$(FLEX) lexer.l

analizador: lex.yy.c
	$(CC) $(CFLAGS) -o analizador lex.yy.c -lfl

clean:
	rm -f analizador lex.yy.c

.PHONY: all clean
