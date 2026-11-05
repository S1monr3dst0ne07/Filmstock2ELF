
from dataclasses import dataclass as dc
import opcodes
import struct


@dc
class Node:
	opcode : int
	arg1   : int
	arg2   : int
	arg3   : int 

	def __repr__(self):
		return f"<{self.opcode.name} {self.arg1}, {self.arg2}, {self.arg3}>"

	# target node for JUMP and JUMP_IF
	target   : "Node" = None

	# node is referenced by jump
	is_refed : bool = False

	# node has been stripped by optimizer,
	# but must remain because it's referenced
	is_stripped : bool = False

	@classmethod
	def parse(cls, read_bytes):
		return cls(
			opcode = opcodes.Opcode(read_bytes(4)),
			arg1   = read_bytes(4),
			arg2   = read_bytes(4),
			arg3   = read_bytes(4),
		)

	def resolve(self, nodes, init):
		target_idx = None

		match self.opcode:
			case opcodes.Opcode.JUMP   : target_idx = self.arg1
			case opcodes.Opcode.JUMP_IF: target_idx = self.arg2

		if target_idx is None: return
		if target_idx not in init:
			print("indirect jumps not supporsed.")
			sys.exit(1)

		value = int(struct.unpack('d', init[target_idx].to_bytes(8, 'little'))[0])

		self.target = nodes[value]
		self.target.is_refed = True


	def compile(self, ctx):
		ptr1 = (arg1 := self.arg1) * 8
		ptr2 = (arg2 := self.arg2) * 8
		ptr3 = (arg3 := self.arg3) * 8

		if self.is_refed:
			ctx.emit(f"inst_{id(self)}:")
		if self.is_stripped:
			return

		def base_arith(inst):
			ctx.emit(f"movq xmm0, [film + {ptr1}]")
			ctx.emit(f"movq xmm1, [film + {ptr2}]")
			ctx.emit(f"{inst}")
			ctx.emit(f"movq [film + {ptr3}], xmm0")

		Opcode = opcodes.Opcode
		match self.opcode:
			case Opcode.COPY:
				ctx.emit(f"movq xmm0, [film + {ptr1}]")
				ctx.emit(f"movq [film + {ptr2}], xmm0")

			case Opcode.ADD     : base_arith("addsd xmm0, xmm1")
			case Opcode.SUBTRACT: base_arith("subsd xmm0, xmm1")
			case Opcode.MULTIPLY: base_arith("mulsd xmm0, xmm1")
			case Opcode.DIVIDE  : base_arith("divsd xmm0, xmm1")
			case Opcode.NOT     :
				ctx.emit(f"movq xmm0, [film+{ptr1}]")
				ctx.emit("pxor xmm1, xmm1")
				ctx.emit("cmpsd xmm0, xmm1, 0")

				ctx.emit("movq  xmm2, [_float_one]")
				ctx.emit("andpd xmm0, xmm2")
				ctx.emit(f"movq [film + {ptr2}], xmm0")

			case Opcode.ITERATE : 
				ctx.emit(f"movq  xmm0, [film + {ptr1}]")
				ctx.emit(f"addsd xmm0, [_float_one]")
				ctx.emit(f"movq  [film + {ptr1}], xmm0")

			case Opcode.END:
				ctx.emit("mov rax, 60")
				ctx.emit("mov rdi,  0")
				ctx.emit("syscall")

			case Opcode.JUMP: 
				ctx.emit(f"jmp inst_{id(self.target)}")
			case Opcode.JUMP_IF: 
				ctx.emit(f"pxor xmm0, xmm0")
				ctx.emit(f"ucomisd xmm0, [film+{ptr1}]")
				ctx.emit(f"jne inst_{id(self.target)}")

			case Opcode.IS_GREATER:
				ctx.emit(f"movq xmm0, [film + {ptr1}]")
				ctx.emit(f"movq xmm1, [film + {ptr2}]")
				ctx.emit("cmpsd xmm0, xmm1, 14")

				ctx.emit("movq  xmm2, [_float_one]")
				ctx.emit("andpd xmm0, xmm2")
				ctx.emit(f"movq [film + {ptr3}], xmm0")
			case Opcode.IS_EQUAL  : 
				ctx.emit(f"movq xmm0, [film + {ptr1}]")
				ctx.emit(f"movq xmm1, [film + {ptr2}]")
				ctx.emit("cmpsd xmm0, xmm1,  0")

				ctx.emit("movq  xmm2, [_float_one]")
				ctx.emit("andpd xmm0, xmm2")
				ctx.emit(f"movq [film + {ptr3}], xmm0")

			case x:
				ctx.runtime_call(x.name, [arg1, arg2, arg3])


