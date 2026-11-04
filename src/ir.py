
from dataclasses import dataclass as dc
import opcodes


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

	@classmethod
	def parse(cls, read_bytes):
		return cls(
			opcode = opcodes.Opcode(read_bytes(4)),
			arg1   = read_bytes(4),
			arg2   = read_bytes(4),
			arg3   = read_bytes(4),
		)

	def resolve(self, nodes):
		target_idx = None

		match self.opcode:
			case opcodes.Opcode.JUMP   : target_idx = self.arg1
			case opcodes.Opcode.JUMP_IF: target_idx = self.arg2

		if target_idx is None: return

		self.target = nodes[target_idx]
		self.target.is_refed = True

@dc
class NodeList:
	nodes : list[Node]

	@classmethod
	def parse(cls, node_count, read_bytes):
		return cls([
			Node.parse(read_bytes)
			for _ in range(node_count)
		])

	def __post_init__(self):
		for node in self.nodes:
			node.resolve(self.nodes)
		
	def compile(self, ctx):
		for node in self.nodes:
			node.compile(ctx)

	def optimize(self):
		# defer-copy optimization
		aliases = {}

		def mat(idx):
			# materialize presisting copied
			for dst, src in aliases.items():
				self.nodes.insert(idx, Node(
					opcode = opcodes.Opcode.COPY,
					arg1   = src,
					arg2   = dst,
					arg3   = None,
				))

		def lookup(idx):
			# follow links back to true source
			while idx in aliases:
				idx = aliases[idx]
			return idx

		idx = 0
		while idx < len(self.nodes):
			node = self.nodes[idx]
			idx += 1

			match node.opcode.name.lower():
				case "copy":
					if node.arg1 != node.arg2:
						aliases[node.arg2] = lookup(node.arg1)
					self.nodes.remove(node)
					idx -= 1

				case "add"      |\
					 "subtract" |\
					 "multiply" |\
					 "divide"   :
					node.arg1 = lookup(node.arg1)
					node.arg2 = lookup(node.arg2)
					del aliases[node.arg3]

				case x:
					mat(idx-1)
					idx += len(aliases)
					aliases.clear()


