
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


	def compile(self, ctx, regs):
		ptr1 = (arg1 := self.arg1) * 8
		ptr2 = (arg2 := self.arg2) * 8
		ptr3 = (arg3 := self.arg3) * 8

		if self.is_refed:
			regs.fence(ctx)
			ctx.emit(f"inst_{id(self)}:")
		if self.is_stripped:
			return

		def base_arith(op):
			reg1 = regs.load(ctx, ptr1)
			reg2 = regs.load(ctx, ptr2)
			ctx.emit(f"{op} xmm{reg1}, xmm{reg2}")
			regs.store(ctx, ptr3, reg1)

		Opcode = opcodes.Opcode
		match self.opcode:
			case Opcode.COPY:
				reg = regs.load(ctx, ptr1)
				regs.store(ctx, ptr2, reg)

			case Opcode.ADD     : base_arith("addsd")
			case Opcode.SUBTRACT: base_arith("subsd")
			case Opcode.MULTIPLY: base_arith("mulsd")
			case Opcode.DIVIDE  : base_arith("divsd")
			case Opcode.NOT     :
				reg1 = regs.load(ctx, ptr1)
				reg2 = regs.new_reg(ctx)

				ctx.emit(f"pxor  xmm{reg2}, xmm{reg2}")
				ctx.emit(f"cmpsd xmm{reg1}, xmm{reg2}, 0")

				reg3 = regs.new_reg(ctx)
				ctx.emit(f"movq  xmm{reg3}, [_float_one]")
				ctx.emit(f"andpd xmm{reg1}, xmm{reg3}")

				regs.store(ctx, ptr2, reg1)

			case Opcode.ITERATE : 
				reg = regs.load(ctx, ptr1)
				ctx.emit(f"addsd xmm{reg}, [_float_one]")
				regs.store(ctx, ptr1, reg)

			case Opcode.END:
				ctx.emit("mov rax, 60")
				ctx.emit("mov rdi,  0")
				ctx.emit("syscall")

			case Opcode.JUMP: 
				regs.fence(ctx)
				ctx.emit(f"jmp inst_{id(self.target)}")
			case Opcode.JUMP_IF: 
				regs.fence(ctx)
				reg = regs.new_reg(ctx)
				ctx.emit(f"pxor xmm{reg}, xmm{reg}")
				ctx.emit(f"ucomisd xmm{reg}, [film+{ptr1}]")
				ctx.emit(f"jne inst_{id(self.target)}")

			case Opcode.IS_GREATER:
				reg1 = regs.load(ctx, ptr1)
				reg2 = regs.load(ctx, ptr2)
				ctx.emit(f"cmpsd xmm{reg1}, xmm{reg2}, 14")

				reg3 = regs.new_reg(ctx)
				ctx.emit(f"movq  xmm{reg3}, [_float_one]")
				ctx.emit(f"andpd xmm{reg1}, xmm{reg3}")
				regs.store(ctx, ptr3, reg1)
			case Opcode.IS_EQUAL: 
				reg1 = regs.load(ctx, ptr1)
				reg2 = regs.load(ctx, ptr2)
				ctx.emit(f"cmpsd xmm{reg1}, xmm{reg2}, 0")

				reg3 = regs.new_reg(ctx)
				ctx.emit(f"movq  xmm{reg3}, [_float_one]")
				ctx.emit(f"andpd xmm{reg1}, xmm{reg3}")
				regs.store(ctx, ptr3, reg1)

			case x:
				regs.fence(ctx)
				ctx.runtime_call(x.name, [arg1, arg2, arg3])


