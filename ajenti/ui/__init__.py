from ajenti.api import *


@interface
class UIElement (object):
	id = None

	def __init__(self):
		self.children = []

	def render(self):
		return {
			'id': self.id,
			'children': self.children,
		}


class UI (object):
	def __init__(self):
		pass

	def create(self, id, *args, **kwargs):
		for cls in UIElement.get_classes():
			if cls.id == id:
				return cls(*args, **kwargs)

	def render(self):
		return self.root.render()


__all__ = [UI, UIElement]