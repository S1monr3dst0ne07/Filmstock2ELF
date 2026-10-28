
run: .FORCE main
	./main

main: .FORCE build.o runtime.o
	ld  -o main build.o runtime.o \
		-z execstack

build.o: .FORCE
	python3 main.py
	fasm build.asm build.o

runtime.o: .FORCE runtime.c
	gcc -g3 -c -o runtime.o runtime.c

.FORCE:
