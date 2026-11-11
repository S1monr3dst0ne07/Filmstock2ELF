
from dataclasses import dataclass as dc
import irnode
import opcodes
from regs import Regs

@dc
class NodeList:
	nodes : list[irnode.Node]

	@classmethod
	def parse(cls, node_count, read_bytes):
		return cls([
			irnode.Node.parse(read_bytes)
			for _ in range(node_count)
		])

	def resolve(self, init):
		for node in self.nodes:
			node.resolve(self.nodes, init)
		
	def compile(self, ctx):
		regs = Regs()

		for node in self.nodes:
			node.compile(ctx, regs)

	def optimize(self):
		# defer-copy optimization
		aliases = {}
		idx = 0

		def mat():
			# materialize presisting copies
			nonlocal idx

			for dst, src in aliases.items():
				self.nodes.insert(idx, irnode.Node(
					opcode = opcodes.Opcode.COPY,
					arg1   = src,
					arg2   = dst,
					arg3   = 0,
				))

			idx += len(aliases)
			aliases.clear()

		def lookup(idx):
			# follow links back to true source
			while idx in aliases:
				idx = aliases[idx]
			return idx

		while idx < len(self.nodes):
			node = self.nodes[idx]

			if node.is_refed:
				mat()

			match node.opcode.name.lower():
				case "copy":
					dst, src = node.arg2, lookup(node.arg1)
					if dst != src: aliases[dst] = src
					node.is_stripped = True

				case "add"      |\
					 "subtract" |\
					 "multiply" |\
					 "divide"   :
					node.arg1 = lookup(node.arg1)
					node.arg2 = lookup(node.arg2)

					if node.arg3 in aliases:
						del aliases[node.arg3]

				case x:
					mat()

			idx += 1



