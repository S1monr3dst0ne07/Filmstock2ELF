
SHELL := /bin/bash

TARGET := prg/3d_renderer/main.fss
#TARGET := prg/test.fss
#TARGET := prg/benchmark.fss

run: .FORCE main
	time ./main

main: .FORCE build.o runtime.o
	cc -o main       \
		-z execstack \
		build.o      \
		runtime.o    \
		-lm \
		-lraylib -lX11 \

build.o: .FORCE target.fs
	python3 src/main.py target.fs
	fasm build.asm build.o -m 1000000

target.fs: .FORCE
	java -jar Filmstock.jar -build $(TARGET) target.fs 
	-rm target.fsdbi

runtime.o: .FORCE runtime.c
	cc -g3 -c -o runtime.o runtime.c

.FORCE:
