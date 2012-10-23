from lxml import etree
import os

from ajenti.plugins import manager


class Inflater:
    def __init__(self, ui):
        self.ui = ui
        self.cache = {}

    def inflate(self, layout):
        if not layout in self.cache:
            plugin, path = layout.split(':')
            file = open(os.path.join(manager.resolve_path(plugin), 'layout', path + '.xml'), 'r')
            self.cache[layout] = etree.parse(file)
        return self.inflate_rec(self.cache[layout].getroot())

    def inflate_rec(self, node):
        tag = node.tag.replace('{', '').replace('}', ':')
        cls = self.ui.get_class(tag)
        props = {}

        for key in node.attrib:
            value = node.attrib[key]
            for prop in cls._properties:
                if prop.name == key:
                    if prop.type in [int, float, unicode, eval]:
                        value = prop.type(value)
                    elif prop.type == bool:
                        value = value == 'True'
                    props[key] = value
                    break
            else:
                raise Exception('Invalid property: %s' % key)

        children = list(self.inflate_rec(child) for child in node)
        element = self.ui.create(tag, children=children, **props)
        return element
