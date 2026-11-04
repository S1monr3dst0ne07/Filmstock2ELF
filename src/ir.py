
from dataclasses import dataclass as dc
import opcodes


@dc
class Node:
	opcode : int
	arg1   : int
	arg2   : int
	arg3   : int 


	prev   : "Node" = None
	next   : "Node" = None

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

	def resolve(self):
		for node in self.nodes:
			node.resolve(self.nodes)

