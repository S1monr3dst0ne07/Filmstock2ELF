
run: .FORCE main
	./main

main: .FORCE build.o runtime.o
	cc -o main     \
		build.o    \
		runtime.o  \
		-lm
		

build.o: .FORCE
	python3 main.py prg/list_basics.fs
	#python3 main.py prg/3d_renderer.fs
	fasm build.asm build.o

runtime.o: .FORCE runtime.c
	cc -g3 -c -o runtime.o runtime.c

.FORCE:
