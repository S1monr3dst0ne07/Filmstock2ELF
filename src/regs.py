
from dataclasses import dataclass as dc
from dataclasses import field

@dc
class Assoc:
	ptr	: int
	reg : int

	# are the register and its
	# assoicated memory address
	# synchronized?
	synced : bool = True

	def read(self, ctx):
		ctx.emit(f"movq xmm{self.reg}, [film + {self.ptr}]")

	def write(self, ctx):
		ctx.emit(f"movq [film + {self.ptr}], xmm{self.reg}")

	def sync(self, ctx):
		if not self.synced:
			self.write(ctx)

		self.synced = True

@dc
class Regs:
	assocs : list[Assoc] = field(default_factory = lambda: [])


	def get_reg_used(self):
		return set(a.reg for a in self.assocs)
	def get_reg_free(self):
		U = set(range(16))
		return U - self.get_reg_used()

	def lookup(self, predicate):
		return next(
			filter(predicate, self.assocs),
			None
		)

	def lookup_ptr(self, ptr):
		return self.lookup(lambda x: x.ptr == ptr)
	def lookup_reg(self, reg):
		return self.lookup(lambda x: x.reg == reg)

	def new_reg(self, ctx):
		# flush a single register,
		# if none available.
		if len(self.assocs) == 16:
			self.assocs.pop(0).write(ctx)

		return next(iter(self.get_reg_free()))

	def load(self, ctx, ptr):
		res = self.lookup_ptr(ptr)
		if res is not None: return res.reg

		assoc = Assoc(ptr, self.new_reg(ctx))
		assoc.read(ctx)
		self.assocs.append(assoc)

		return assoc.reg

	def store(self, ctx, ptr, reg):
		reg_assoc = self.lookup_reg(reg)
		reg_assoc.sync(ctx)

		ptr_assoc = self.lookup(lambda x: 
			x.ptr == ptr and x.reg != reg)

		if ptr_assoc is not None:
			# we are writing into a pointer,
			# which is already loaded.
			# we can drop this association
			# without sync because the content
			# of the referenced memory address
			# is changed.
			self.assocs.remove(ptr_assoc)

		reg_assoc.synced = False
		reg_assoc.ptr     = ptr

	def fence(self, ctx):
		for assoc in self.assocs:
			assoc.sync(ctx)
		self.assocs = []




