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

		node_list.resolve()

		return cls(film_len, film_init_values, node_list)

