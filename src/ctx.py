
from dataclasses import dataclass as dc
from dataclasses import field


@dc
class Ctx:
	output      : list = field(default_factory=lambda: [])
	extern_syms : set  = field(default_factory=lambda: set())

	def emit(self, x):
		self.output.append(x)

	def runtime_call(self, name, arg):
		fn_name = f"rt_{name.lower()}"
		self.extern_syms.add(fn_name)

		emit(f"mov rdi, {arg[1]}")
		emit(f"mov rsi, {arg[2]}")
		emit(f"mov rdx, {arg[3]}")
		emit(f"call {fn_name}")

	def mark_extern(self):
		for sym in self.extern_syms:
			self.emit(f"extrn {sym}")

		





