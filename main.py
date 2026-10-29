
from dataclasses import dataclass as dc
from enum import Enum, auto
import subprocess
import sys

class Opcode(Enum):
	COPY                    = 0
	ADD                     = auto()
	SUBTRACT                = auto()
	MULTIPLY                = auto()
	DIVIDE                  = auto()
	SQUARE_ROOT             = auto()
	SIN                     = auto()
	COS                     = auto()
	TAN                     = auto()
	ASIN                    = auto()
	ACOS                    = auto()
	ATAN2                   = auto()
	POWER                   = auto()
	MOD                     = auto()
	IS_EQUAL                = auto()
	IS_GREATER              = auto()
	NOT                     = auto()
	AND                     = auto()
	OR                      = auto()
	JUMP_IF                 = auto()
	PRINT                   = auto()
	PRINT_NUMBERS           = auto()
	ITERATE                 = auto()
	COPY_FROM               = auto()
	POINTER                 = auto()
	POSITION                = auto()
	JUMP                    = auto()
	END                     = auto()
	FLOOR                   = auto()
	ROUND                   = auto()
	CEIL                    = auto()
	TIME                    = auto()
	NEW_LIST                = auto()
	COPY_FROM_LIST          = auto()
	LENGTH_OF_LIST          = auto()
	LIST_AMOUNT             = auto()
	ADD_LIST                = auto()
	REMOVE_AT_LIST          = auto()
	EMPTY_LIST              = auto()
	REMOVE_ALL_LISTS        = auto()
	ADD_AT_LIST             = auto()
	REVERSE_LIST            = auto()
	SHUFFLE_LIST            = auto()
	SORT_LIST               = auto()
	SLEEP                   = auto()
	RANDOM                  = auto()
	INPUT                   = auto()
	LIST_SET                = auto()
	UPDATE_CONSOLE          = auto()
	PRINT_VECTOR            = auto()
	PRINT_VECTOR_NUMBERS    = auto()
	PRINT_VECTOR_SEPARATED  = auto()
	SET_COLOR               = auto()
	SET_POSITION            = auto()
	SET_TEXT_SIZE           = auto()
	DRAW_TRIANGLES          = auto()
	DRAW_TEXT               = auto()
	BEGIN_DRAWING           = auto()
	END_DRAWING             = auto()
	IS_PRESSED              = auto()
	MOUSE_PRESSED           = auto()
	GET_MOUSE_X             = auto()
	GET_MOUSE_Y             = auto()
	GET_SCROLL              = auto()
	GET_WIDTH               = auto()
	GET_HEIGHT              = auto()
	LIST_LOAD               = auto()
	LIST_STORE              = auto()


@dc
class IrNode:
	opcode : int
	arg1   : int
	arg2   : int
	arg3   : int

	def compile(node, emit, file):
		ptr1 = (arg1 := node.arg1) * 8
		ptr2 = (arg2 := node.arg2) * 8
		ptr3 = (arg3 := node.arg3) * 8

		def base_arith(inst):
			emit(f"movq xmm0, [film + {ptr1}]")
			emit(f"movq xmm1, [film + {ptr2}]")
			emit(f"{inst}")
			emit(f"movq [film + {ptr3}], xmm0")

		def runtime_call(name):
			emit(f"mov rdi, {arg1}")
			emit(f"mov rsi, {arg2}")
			emit(f"mov rdx, {arg3}")
			emit(f"call {name}")

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
				emit(f"movq xmm0, [film+{arg1}]")
				emit("movq xmm1, [_float_zero]")
				emit("cmpsd xmm0, xmm1, 0")
				emit(f"movq [film+{arg1}], xmm0")
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
				emit(f"mov rax, [film+{arg1}]")
				emit(f"test rax, rax")
				emit(f"jnz inst_{jmp_decode(arg2)}")

			case Opcode.IS_GREATER: base_arith("cmpsd xmm0, xmm1, 14")
			case Opcode.IS_EQUAL  : base_arith("cmpsd xmm0, xmm1,  0")

			case Opcode.PRINT         : runtime_call("print")
			case Opcode.PRINT_NUMBERS : runtime_call("print_numbers")
			case Opcode.UPDATE_CONSOLE: runtime_call("update_console")

			case Opcode.POWER         : runtime_call("power")
			case Opcode.MOD           : runtime_call("modulo")
			case Opcode.SIN           : runtime_call("_sin")
			case Opcode.COS           : runtime_call("_cos")
			case Opcode.TAN           : runtime_call("_tan")
			case Opcode.FLOOR         : runtime_call("_floor")
			case Opcode.CEIL          : runtime_call("_ceil")
			case Opcode.SQUARE_ROOT   : runtime_call("_sqrt")

			case Opcode.NEW_LIST             : runtime_call("new_list")
			case Opcode.EMPTY_LIST           : runtime_call("empty_list")
			case Opcode.ADD_LIST             : runtime_call("add_list")
			case Opcode.PRINT_VECTOR         : runtime_call("print_list")
			case Opcode.PRINT_VECTOR_NUMBERS : runtime_call("print_list_numbers")
			case Opcode.SORT_LIST            : runtime_call("sort_list")
			case Opcode.COPY_FROM_LIST       : runtime_call("copy_from_list")
			case Opcode.LIST_SET             : runtime_call("list_set")
			case Opcode.LENGTH_OF_LIST       : runtime_call("list_length")

			case Opcode.TIME                 : runtime_call("_time")


			case x:
				print(f"opcode {x} not implemented.")

@dc
class FsFile:
	film_len         : int
	film_init_values : list[int]
	insts            : list[IrNode]

	@classmethod
	def parse(cls, path):
		with open(path, 'rb') as f:
			raw = bytearray(f.read())

		read_idx = 0
		def read_bytes(n=1):
			nonlocal read_idx
			value = raw[read_idx : read_idx+n]
			read_idx += n
			return int.from_bytes(value, 'little')

		def check_margin():
			return all(
				x == 0xff for x in
				raw[read_idx : read_idx + 64]
			)

		film_len = read_bytes(4)

		# map index -> int encoded double
		film_init_values = {}
		while not check_margin():
			index = read_bytes(4)
			film_init_values[index] = read_bytes(8)

		read_idx += 64

		inst_buffer_len = len(raw) - read_idx
		assert inst_buffer_len % 16 == 0

		insts_len = inst_buffer_len // 16
		insts = []
		for _ in range(insts_len):
			insts.append(IrNode(
				opcode = Opcode(read_bytes(4)),
				arg1   =        read_bytes(4),
				arg2   =        read_bytes(4),
				arg3   =        read_bytes(4),
			))

		return cls(film_len, film_init_values, insts)

	def compile(self):
		output = []
		emit = lambda x: output.append(x)

		# headers
		emit("format ELF64")
		emit("extrn print")
		emit("extrn print_numbers")
		emit("extrn update_console")

		emit("extrn power")
		emit("extrn modulo")
		emit("extrn _sin")
		emit("extrn _cos")
		emit("extrn _tan")
		emit("extrn _floor")
		emit("extrn _ceil")
		emit("extrn _sqrt")

		emit("extrn new_list")
		emit("extrn add_list")
		emit("extrn empty_list")
		emit("extrn print_list")
		emit("extrn print_list_numbers")
		emit("extrn sort_list")
		emit("extrn copy_from_list")
		emit("extrn list_set")
		emit("extrn list_length")

		emit("extrn _time")

		emit("public film")
		emit("public _compiled_entry")

		emit("section '.text'")
		emit("_compiled_entry:")
		emit("add rsp, 8") #remove caller address

		for idx, inst in enumerate(self.insts):
			emit(f"inst_{idx}:")
			inst.compile(emit, self)

		# exit(0)
		emit("mov rax, 60")
		emit("mov rdi, 0")
		emit("syscall")

		# film
		emit("section '.data'")
		emit("film:")
		for i in range(self.film_len):
			value = self.film_init_values.get(i) or 0
			emit(f"dq {value}")

		emit("_float_one : dq 1.0")
		emit("_float_zero: dq 0.0")

		return '\n'.join(output)

			
def build(asm):
	with open("build.asm", 'w') as f:
		f.write(asm)


def main():
	file = FsFile.parse(sys.argv[1])
	asm = file.compile()

	build(asm)


if __name__ == '__main__':
	main()

