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
	def __init__(self, object, field, ui, property=None):
		Binding.__init__(self, object, field, ui)
		if property is None:
			for prop in ui.properties.values():
				if type(self.get()) in prop.bindtypes:
					print self.object, self.field, type(self.get()) , prop.bindtypes
					self.property = prop.name
		else:
			self.property = property

	def populate(self):
		self.ui.properties[self.property].value = self.get()

	def update(self):
		self.set(self.ui.properties[self.property].value)


class CollectionAutoBinding (Binding):
	def __init__(self, object, field, ui, info):
		Binding.__init__(self, object, field, ui)
		self.info = info
		self.binders = {}

	def populate(self):
		self.values = self.info.values(getattr(self.object, self.field))
		self.items_ui = self.ui.find('__items') or self.ui
		self.items_ui.empty()
		for value in self.values:
			template = self.info.template(value)
			self.items_ui.append(template)
			binder = Binder(value, template)
			binder.autodiscover()
			binder.populate()
			self.binders[value] = binder

			del_button = template.find('__delete')
			if del_button:
				del_button.on('click', self.on_delete, value)


		add_button = self.ui.find('__add')
		if add_button is not None:
			add_button.on('click', self.on_add)

	def on_add(self):
		self.update()
		self.info.add_item(self.info.new_item())
		self.populate()
		self.ui.publish()

	def on_delete(self, item):
		self.update()
		self.info.delete_item(item)
		self.populate()
		self.ui.publish()

	def update(self):
		for value in self.values:
			self.binders[value].update()
		

class CollectionBindInfo (object):
	def __init__(self, 
				binding=CollectionAutoBinding, 
				template=lambda x : None, 
				values=lambda x : x,
				new_item=lambda : None,
				add_item=lambda x : None,
				delete_item=lambda x : None,
				):	
		self.template = template
		self.values = values
		self.binding = binding
		self.add_item = add_item
		self.delete_item = delete_item
		self.new_item = new_item


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
				if type(v) in [str, unicode, int, float, bool, property]:
					self.add(PropertyBinding(object, k, child))
				elif type(v) not in [dict, list, tuple]:
					self.autodiscover(v, child)
				else:
					if not hasattr(object, k + '__bind'):
						raise Exception('Collection lacks binding info (%s__bind)' % k)
					info = getattr(object, k + '__bind')
					self.add(info.binding(object, k, child, info))

	def add(self, binding):
		self.bindings.append(binding)

	def populate(self):
		for binding in self.bindings:
			binding.populate()

	def update(self):
		for binding in self.bindings:
			binding.update()

