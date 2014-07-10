from lxml import etree
import os
import logging

import ajenti
from ajenti.api import plugin, BasePlugin, persistent, rootcontext
from ajenti.plugins import manager
from ajenti.ui.element import UIProperty, UIElement, NullElement
from ajenti.util import *
#from ajenti.profiler import *


@public
class TemplateNotFoundError (Exception):
    pass


@public
@persistent
@rootcontext
@plugin
class Inflater (BasePlugin):
    def init(self):
        self.parser = etree.XMLParser()
        self.cache = {}
        self._element_cache = {}

    def precache(self):
        from ajenti.ui import UI
        temp_ui = UI.new()
        for plugin in manager.get_order():
            layout_dir = os.path.join(manager.resolve_path(plugin), 'layout')
            if os.path.exists(layout_dir):
                for layout in os.listdir(layout_dir):
                    layout_name = os.path.splitext(layout)[0]
                    if layout_name:
                        layout = '%s:%s' % (plugin, layout_name)
                        logging.debug('Precaching layout %s' % layout)
                        self.inflate(temp_ui, layout)

    def create_element(self, ui, typeid, *args, **kwargs):
        """
        Creates an element by its type ID.
        """
        cls = self.get_class(typeid)
        inst = cls.new(ui, context=(ui or self).context, *args, **kwargs)
        inst.typeid = typeid
        return inst

    def get_class(self, typeid):
        """
        :returns: element class by element type ID
        """
        if typeid in self._element_cache:
            return self._element_cache[typeid]
        for cls in UIElement.get_classes():
            if cls.typeid == typeid:
                self._element_cache[typeid] = cls
                return cls
        else:
            self._element_cache[typeid] = NullElement
            return NullElement

    def inflate(self, ui, layout):
        if not layout in self.cache or ajenti.debug:
            plugin, path = layout.split(':')
            try:
                file = open(os.path.join(manager.resolve_path(plugin), 'layout', path + '.xml'), 'r')
            except IOError as e:
                raise TemplateNotFoundError(e)
            data = file.read()
            data = """<xml xmlns:bind="bind" xmlns:binder="binder">%s</xml>""" % data
            xml = etree.fromstring(data, parser=self.parser)[0]
            self.cache[layout] = self.inflate_rec(ui, xml)
        layout = self.cache[layout].clone(set_ui=ui, set_context=(ui or self).context)
        return layout

    def inflate_rec(self, ui, node):
        if callable(node.tag):
            # skip comments
            return None

        tag = node.tag.replace('{', '').replace('}', ':')

        if tag == 'include':
            return self.inflate(ui, node.attrib['layout'])

        cls = self.get_class(tag)
        props = {}
        extra_props = {}

        for key in node.attrib:
            value = node.attrib[key]
            if value.startswith('{') and value.endswith('}'):
                value = _(value[1:-1])
            value = value.replace('\\n', '\n')
            for prop in cls._properties.values():
                if prop.name == key:
                    if prop.type in [int, float, unicode, eval]:
                        value = prop.type(value)
                    elif prop.type in [list, dict]:
                        value = eval(value)
                    elif prop.type == bool:
                        value = value == 'True'
                    props[key] = value
                    break
            else:
                extra_props[key] = value

        children = filter(None, list(self.inflate_rec(ui, child) for child in node))
        element = self.create_element(ui, tag, children=children, **props)
        for k, v in extra_props.iteritems():
            element.property_definitions[k] = UIProperty(name=k, public=False)
            element.properties[k] = v
        return element
