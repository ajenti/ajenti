from lxml import etree
import os

import ajenti
from ajenti.plugins import manager
from ajenti.util import *


@public
class TemplateNotFoundError (Exception):
    pass


@public
class Inflater:
    def __init__(self, ui):
        self.ui = ui
        self.cache = {}

    def inflate(self, layout):
        if not layout in self.cache:
            plugin, path = layout.split(':')
            try:
                file = open(os.path.join(manager.resolve_path(plugin), 'layout', path + '.xml'), 'r')
            except IOError, e:
                raise TemplateNotFoundError(e)
            if not ajenti.debug:
                self.cache[layout] = etree.parse(file)
        return self.inflate_rec(self.cache[layout].getroot())

    def inflate_rec(self, node):
        tag = node.tag.replace('{', '').replace('}', ':')

        if tag == 'include':
            return self.inflate(node.attrib['layout'])

        cls = self.ui.get_class(tag)
        props = {}

        for key in node.attrib:
            value = node.attrib[key]
            for prop in cls._properties:
                if prop.name == key:
                    if prop.type in [int, float, unicode, eval]:
                        value = prop.type(value)
                    elif prop.type in [list]:
                        value = eval(value)
                    elif prop.type == bool:
                        value = value == 'True'
                    props[key] = value
                    break
            else:
                raise Exception('Invalid property: %s' % key)

        children = list(self.inflate_rec(child) for child in node)
        element = self.ui.create(tag, children=children, **props)
        return element
