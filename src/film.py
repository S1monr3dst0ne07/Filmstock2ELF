from dataclasses import dataclass as dc

import ir

@dc
class Film:
	length : int
	init   : list[int]

	nodes  : ir.NodeList

	@classmethod
	def load(cls, path):
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

		node_buffer_len = len(raw) - read_idx
		assert node_buffer_len % 16 == 0

		node_count = node_buffer_len // 16
		node_list = ir.NodeList.parse(node_count, read_bytes)
		node_list.resolve(film_init_values)

		return cls(film_len, film_init_values, node_list)


	def compile(self, ctx):
		ctx.emit("format ELF64")
		ctx.emit("public film")
		ctx.emit("public _compiled_entry")

		ctx.emit("section '.text'")
		ctx.emit("_compiled_entry:")
		ctx.emit("add rsp, 8") #remove caller address

		self.nodes.compile(ctx)
		ctx.mark_extern()

		# exit(0)
		ctx.emit("mov rax, 60")
		ctx.emit("mov rdi, 0")
		ctx.emit("syscall")

		# film
		ctx.emit("section '.data'")
		ctx.emit("film:")
		for i in range(self.length):
			value = self.init.get(i) or 0
			ctx.emit(f"dq {value}")

		ctx.emit("_float_one: dq 1.0")


