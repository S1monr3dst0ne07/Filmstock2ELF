
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


		def int2float(ptr):
			ctx.emit(f"cvtsi2sd xmm1, [film + {ptr}]")
			ctx.emit(f"movq     [film + {ptr}], xmm1")
		def normalize(ptr):
			ctx.emit(f"and qword [film + {ptr}], 1")

		def jmp_decode(idx):
			return value

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
				ctx.emit(f"movq [film+{ptr2}], xmm0")
				normalize(ptr2)
				int2float(ptr2)
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
				base_arith("cmpsd xmm0, xmm1, 14")
				normalize(ptr3)
				int2float(ptr3)
			case Opcode.IS_EQUAL  : 
				base_arith("cmpsd xmm0, xmm1,  0")
				normalize(ptr3)
				int2float(ptr3)

			case x:
				ctx.runtime_call(x.name, [arg1, arg2, arg3])






		

@dc
class NodeList:
	nodes : list[Node]

	@classmethod
	def parse(cls, node_count, read_bytes):
		return cls([
			Node.parse(read_bytes)
			for _ in range(node_count)
		])

	def resolve(self, init):
		for node in self.nodes:
			node.resolve(self.nodes, init)
		
	def compile(self, ctx):
		for node in self.nodes:
			node.compile(ctx)

#	def optimize(self):
#		# defer-copy optimization
#		aliases = {}
#		idx = 0
#
#		def mat():
#			# materialize presisting copies
#			nonlocal idx
#
#			for dst, src in aliases.items():
#				self.nodes.insert(idx, Node(
#					opcode = opcodes.Opcode.COPY,
#					arg1   = src,
#					arg2   = dst,
#					arg3   = 0,
#				))
#
#			idx += len(aliases)
#			aliases.clear()
#
#		def lookup(idx):
#			# follow links back to true source
#			while idx in aliases:
#				idx = aliases[idx]
#			return idx
#
#		while idx < len(self.nodes):
#			node = self.nodes[idx]
#
#			if node.is_refed:
#				mat()
#
#			match node.opcode.name.lower():
#				case "copy":
#					dst, src = node.arg2, lookup(node.arg1)
#					if dst != src: aliases[dst] = src
#					node.is_stripped = True
#
#				case "add"      |\
#					 "subtract" |\
#					 "multiply" |\
#					 "divide"   :
#					node.arg1 = lookup(node.arg1)
#					node.arg2 = lookup(node.arg2)
#
#					if node.arg3 in aliases:
#						del aliases[node.arg3]
#
#				case x:
#					mat()
#
#			idx += 1
#

