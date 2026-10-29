
run: .FORCE main
	./main

main: .FORCE build.o runtime.o
	cc -o main       \
		-z execstack \
		build.o      \
		runtime.o    \
		-lm
		

build.o: .FORCE
	#python3 main.py prg/3d_renderer.fs
	python3 main.py /tmp/Filmstock/build.filmstock
	fasm build.asm build.o -m 1000000

runtime.o: .FORCE runtime.c
	cc -g3 -c -o runtime.o runtime.c

.FORCE:
