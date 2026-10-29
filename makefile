
run: .FORCE main
	./main

main: .FORCE build.o runtime.o
	cc -o main     \
		build.o    \
		runtime.o  \
		-lm
		

build.o: .FORCE
	python3 main.py /tmp/Filmstock/build.filmstock
	fasm build.asm build.o

runtime.o: .FORCE runtime.c
	cc -g3 -c -o runtime.o runtime.c

.FORCE:
