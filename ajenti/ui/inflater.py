from lxml import etree
import os

from ajenti.plugins import manager

from element import UIElement


class Inflater:
	def __init__(self, ui):
		self.ui = ui
		self.cache = {}

	def inflate(self, layout):
		if not layout in self.cache:
			plugin, path = layout.split(':')
			file = open(os.path.join(manager.resolve_path(plugin), 'layout', path+'.xml'), 'r')
			self.cache[layout] = etree.parse(file)
		return self.inflate_rec(self.cache[layout].getroot())

	def inflate_rec(self, node):
		element = self.ui.create(node.tag)
		for key in node.attrib:
			value = node.attrib[key]
			if key == 'id':
				element.id = value
			else:
				element.properties[key].set(value)
		for child in node:
			element.append(self.inflate_rec(child))
		return element


