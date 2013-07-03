from lxml import etree
import os

import ajenti
from ajenti.plugins import manager
from ajenti.ui.element import UIProperty
from ajenti.util import *
#from ajenti.profiler import *


@public
class TemplateNotFoundError (Exception):
    pass


@public
class Inflater:
    def __init__(self, ui):
        self.ui = ui
        self.parser = etree.XMLParser()
        self.cache = {}

    def inflate(self, layout):
        if not layout in self.cache or ajenti.debug:
            #profile('Inflating %s' % layout)
            plugin, path = layout.split(':')
            try:
                file = open(os.path.join(manager.resolve_path(plugin), 'layout', path + '.xml'), 'r')
            except IOError, e:
                raise TemplateNotFoundError(e)
            data = file.read()
            data = """<xml xmlns:bind="bind" xmlns:binder="binder">%s</xml>""" % data
            xml = etree.fromstring(data, parser=self.parser)[0]
            self.cache[layout] = self.inflate_rec(xml)
        #else:
            #profile('Inflating %s (cached)' % layout)
        layout = self.cache[layout].clone()
        #profile_end()
        return layout

    def inflate_rec(self, node):
        tag = node.tag.replace('{', '').replace('}', ':')

        if tag == 'include':
            return self.inflate(node.attrib['layout'])

        cls = self.ui.get_class(tag)
        props = {}
        extra_props = {}

        for key in node.attrib:
            value = node.attrib[key]
            if value.startswith('{') and value.endswith('}'):
                value = _(value[1:-1])
            for prop in cls._properties.values():
                if prop.name == key:
                    if prop.type in [eval, list, dict]:
                        value = _(value)
                    if prop.type in [int, float, unicode, eval, dict]:
                        value = prop.type(value)
                    elif prop.type in [list]:
                        value = eval(value)
                    elif prop.type == bool:
                        value = value == 'True'
                    props[key] = value
                    break
            else:
                extra_props[key] = value
                #raise Exception('Invalid property: %s' % key)

        children = list(self.inflate_rec(child) for child in node)
        element = self.ui.create(tag, children=children, **props)
        for k, v in extra_props.iteritems():
            element.property_definitions[k] = UIProperty(name=k, public=False)
            element.properties[k] = v
        return element
