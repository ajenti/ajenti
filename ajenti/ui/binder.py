class Binding (object):
	def __init__(self, object, field, ui):
		self.object = object
		self.field = field
		self.ui = ui

	def get(self):
		return getattr(self.object, self.field)

	def set(self, value):
		setattr(self.object, self.field, value)

	def populate(self):
		pass

	def update(self):
		pass


class PropertyBinding (Binding):
	def __init__(self, object, field, ui, property='value'):
		Binding.__init__(self, object, field, ui)
		self.property = property

	def populate(self):
		self.ui.properties[self.property].value = self.get()

	def update(self):
		self.set(self.ui.properties[self.property].value)


class Binder (object):
	def __init__(self, object, ui):
		self.object = object
		self.ui = ui
		self.bindings = []

	def autodiscover(self, object=None, ui=None):
		object = object or self.object
		for k,v in object.__dict__.iteritems():
			child = (ui or self.ui).find(k)
			if child:
				if type(v) in [str, unicode, int, float, bool]:
					self.add(PropertyBinding(object, k, child))
				elif type(v) not in [dict, list, tuple]:
					self.autodiscover(v, child)

	def add(self, binding):
		self.bindings.append(binding)

	def populate(self):
		for binding in self.bindings:
			binding.populate()

	def update(self):
		for binding in self.bindings:
			binding.update()

