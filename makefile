
SHELL := /bin/bash

run: .FORCE main
	#time ./main

main: .FORCE build.o runtime.o
	cc -o main       \
		-z execstack \
		build.o      \
		runtime.o    \
		-lm \
		-lraylib -lX11 \

		

build.o: .FORCE
	python3 src/main.py tmp.fs
	#python3 src/main.py prg/3d_renderer.fs
	fasm build.asm build.o -m 1000000

runtime.o: .FORCE runtime.c
	cc -g3 -c -o runtime.o runtime.c

.FORCE:
