
from dataclasses import dataclass as dc
import subprocess
import sys

import film
import irnode
import irlist
import ctx


def main():
	context = ctx.Ctx()
	fs = film.Film.load(sys.argv[1])
	print(fs.nodes)
	fs.compile(context)

	context.write("build.asm")


if __name__ == '__main__':
	main()

