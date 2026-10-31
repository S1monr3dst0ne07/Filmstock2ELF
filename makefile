
run: .FORCE main
	./main

main: .FORCE build.o runtime.o
	cc -o main       \
		-z execstack \
		build.o      \
		runtime.o    \
		-lm \
		-lraylib -lX11 \

		

build.o: .FORCE
	python3 main.py tmp.fs
	fasm build.asm build.o -m 1000000

runtime.o: .FORCE runtime.c
	cc -g3 -c -o runtime.o runtime.c

.FORCE:
