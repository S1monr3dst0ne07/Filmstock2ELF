
from dataclasses import dataclass as dc


@dc
class IrNode:
	opcode : int
	arg1   : int
	arg2   : int
	arg3   : int


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
			value = int.from_bytes(raw[
				read_idx : read_idx+n
			], 'little')
			read_idx += n
			return value

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

		insts_len = (len(raw) - read_idx) // 4
		insts = []
		for _ in range(insts_len):
			insts.append(IrNode(
				opcode = read_bytes(4),
				arg1   = read_bytes(4),
				arg2   = read_bytes(4),
				arg3   = read_bytes(4),
			))

		return cls(film_len, film_init_values, insts)



def main():
	file = FsFile.parse("prg/3d_renderer.fs")
	print(file.insts[:100])


if __name__ == '__main__':
	main()

