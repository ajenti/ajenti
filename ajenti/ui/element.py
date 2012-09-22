from ajenti.api import *


class UIProperty (object):
	def __init__(self, name, value):
		self.dirty = False
		self.name = name
		self.value = value

	def clone(self):
		return UIProperty(self.name, self.value)

	def get(self):
		return self.value

	def set(self, value):
		self.dirty = self.value != value
		self.value = value


@interface
class UIElement (object):
	typeid = None
	__last_id = 0

	@classmethod
	def __generate_id(cls):
		cls.__last_id += 1
		return cls.__last_id

	def __init__(self, ui, typeid=None, **kwargs):
		self.ui = ui

		if typeid is not None:
			self.typeid = typeid
		
		self.id = UIElement.__generate_id()

		if not hasattr(self, '_properties'):
			self._properties = []
		
		self.children = []
		
		self.properties = {}
		for prop in self._properties:
			self.properties[prop.name] = prop.clone()
		for key in kwargs:
			self.properties[key].set(kwargs[key])
		
		self.events = {}
		self.init()

	def init(self):
		pass

	def find(self, id):
		if self.id == id:
			return self
		for child in self.children:
			found = child.find(id)
			if found:
				return found

	def render(self):
		result = {
			'id': self.id,
			'typeid': self.typeid,
			'events': self.events.keys(),
			'children': [c.render() for c in self.children],
		}
		for prop in self.properties.values():
			result[prop.name] = prop.value
		return result

	def on(self, event, handler):
		self.events[event] = handler

	def publish(self):
		self.ui.queue_update()

	def event(self, event, params=None):
		if event in self.events:
			self.events[event](**(params or {}))

	def append(self, child):
		self.children.append(child)

	def remove(self, child):
		self.children.remove(child)


def p(prop, default=None):
	def decorator(cls):
		prop_obj = UIProperty(prop, value=default)
		if not hasattr(cls, '_properties'):
			cls._properties = []
		cls._properties.append(prop_obj)

		def get(self):
			return self.properties[prop].get()

		def set(self, value):
			return self.properties[prop].set(value)

		setattr(cls, prop, property(get, set))
		return cls
	return decorator