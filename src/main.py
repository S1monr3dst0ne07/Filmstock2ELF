
from dataclasses import dataclass as dc
import subprocess
import sys

from opcodes import Opcode
import film
import ir
import ctx


def compile(node, emit, file):
	ptr1 = (arg1 := node.arg1) * 8
	ptr2 = (arg2 := node.arg2) * 8
	ptr3 = (arg3 := node.arg3) * 8

	def base_arith(inst):
		emit(f"movq xmm0, [film + {ptr1}]")
		emit(f"movq xmm1, [film + {ptr2}]")
		emit(f"{inst}")
		emit(f"movq [film + {ptr3}], xmm0")

	def int2float(ptr):
		emit(f"cvtsi2sd xmm1, [film + {ptr}]")
		emit(f"movq     [film + {ptr}], xmm1")
	def normalize(ptr):
		emit(f"and qword [film + {ptr}], 1")

	def jmp_decode(idx):
		if idx not in file.film_init_values:
			print("indirect jumps not supporsed.")
			sys.exit(1)

		import struct
		real = file.film_init_values[idx]
		value = int(struct.unpack('d', real.to_bytes(8, 'little'))[0])
		return value

	match node.opcode:
		case Opcode.COPY:
			emit(f"movq xmm0, [film + {ptr1}]")
			emit(f"movq [film + {ptr2}], xmm0")

		case Opcode.ADD     : base_arith("addsd xmm0, xmm1")
		case Opcode.SUBTRACT: base_arith("subsd xmm0, xmm1")
		case Opcode.MULTIPLY: base_arith("mulsd xmm0, xmm1")
		case Opcode.DIVIDE  : base_arith("divsd xmm0, xmm1")
		case Opcode.NOT     :
			emit(f"movq xmm0, [film+{ptr1}]")
			emit( "pxor xmm1, xmm1")
			emit("cmpsd xmm0, xmm1, 0")
			emit(f"movq [film+{ptr2}], xmm0")
			normalize(ptr2)
			int2float(ptr2)
		case Opcode.ITERATE : 
			emit(f"movq  xmm0, [film + {ptr1}]")
			emit(f"addsd xmm0, [_float_one]")
			emit(f"movq  [film + {ptr1}], xmm0")

		case Opcode.END:
			emit("mov rax, 60")
			emit("mov rdi,  0")
			emit("syscall")

		case Opcode.JUMP: 
			emit(f"jmp inst_{jmp_decode(arg1)}")
		case Opcode.JUMP_IF: 
			emit(f"pxor xmm0, xmm0")
			emit(f"ucomisd xmm0, [film+{ptr1}]")
			emit(f"jne inst_{jmp_decode(arg2)}")

		case Opcode.IS_GREATER:
			base_arith("cmpsd xmm0, xmm1, 14")
			normalize(ptr3)
			int2float(ptr3)
		case Opcode.IS_EQUAL  : 
			base_arith("cmpsd xmm0, xmm1,  0")
			normalize(ptr3)
			int2float(ptr3)

		case x:
			ctx.runtime_call(x.name, [arg1, arg2, arg3])



def main():
	context = ctx.Ctx()
	fs = film.Film.load(sys.argv[1])
	fs.nodes.optimize()
	print(fs.nodes)
	#fs.compile(context)

	#with open("build.asm", 'w') as f:
	#	f.write(asm)


if __name__ == '__main__':
	main()

