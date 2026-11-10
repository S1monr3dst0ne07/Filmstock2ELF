
from dataclasses import dataclass as dc
import subprocess
import sys

import film
import irnode
import irlist
import ctx

OPTIMIZE = True

def main():
	context = ctx.Ctx()
	fs = film.Film.load(sys.argv[1])
	if OPTIMIZE: fs.nodes.optimize()
	fs.compile(context)

	context.write("build.asm")


if __name__ == '__main__':
	main()

