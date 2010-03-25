import random
import xml.dom.minidom as dom


class Element(dom.Element):
    """ Generate XML element

    @tag - element name
    *args - any number of dictionaries {'attribute':'value'}
    **kwargs - any number of keyword arguments attribute="value"
    """
    visible = True
    def __init__(self, tag, *args, **kwargs):
        dom.Element.__init__(self, tag)
        self.id = str(random.randint(1,9000*9000))
        self._init(*args, **kwargs)

    def _init(self, *args, **kwargs):
        for attr in kwargs:
            self.setAttribute(attr, str(kwargs[attr]))
        for attrs in args:
            if isinstance(attrs, dict):
                # Append attributes in dicts
                for attr in attrs:
                    self.setAttribute(attr, str(attrs[attr]))
            elif isinstance(attrs, dom.Element):
                # Append childs
                self.appendChild(attrs)

    def __getitem__(self, key):
        return self.getAttribute(key)

    def __setitem__(self, key, value):
        self.setAttribute(key, str(value))


class Html(object):
    """ Automatically generate XML tag by calling name

    >>> from ajenti.ui.html import Html
    >>> h = Html()
    >>> h.meta(encoding='ru').toxml()
    '<meta encoding="ru"/>'
    >>>
    """
    def __getattr__(self, name):
        return lambda *args, **kwargs: Element(name, *args, **kwargs)

    def gen(self, name, *args, **kwargs):
        return Element(name, *args, **kwargs)


class UI(object):
    class __metaclass__(type):
        def __getattr__(cls, name):
            return lambda *args, **kwargs: Element(name.lower(), *args, **kwargs)

    @staticmethod
    def VContainer(*args):
        class VContainer(Element):
            """ Container class
            To maintain same syntax with XML Templates - we should use vnode()
            """
            def __init__(self, *args):
                Element.__init__(self, 'vcontainer')
                self.elements = []
                for e in args:
                    if isinstance(e, dom.Element):
                        self.vnode(e)

            def vnode(self, e):
                self.appendChild(Html().vnode(e))

        return VContainer(*args)

    @staticmethod
    def HContainer(*args):
        class HContainer(Element):
            """ Container class
            To maintain same syntax with XML Templates - we should use hnode()
            """
            def __init__(self, *args):
                Element.__init__(self, 'hcontainer')
                self.elements = []
                for e in args:
                    if isinstance(e, dom.Element):
                        self.hnode(e)

            def hnode(self, e):
                self.appendChild(Html().hnode(e))

        return HContainer(*args)

    @staticmethod
    def Text(text):
        return Element('span', {'py:content':"'%s'"%text, 'py:strip':""})

    @staticmethod
    def Option(text='option', **kw):
        el = Element('option', **kw)
        el.appendChild(UI.Text(text))
        return el

