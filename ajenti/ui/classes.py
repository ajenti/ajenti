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
            self.setAttribute(attr, kwargs[attr])
        for attrs in args:
            if isinstance(attrs, dict):
                # Append attributes in dicts
                for attr in attrs:
                    self.setAttribute(attr, attrs[attr])
            elif isinstance(attrs, dom.Element):
                # Append childs 
                self.appendChild(attrs)

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

class Category(Element):
    def __init__(self, *args, **kwargs):
        Element.__init__(self, 'category', *args, **kwargs)
        self._init(id=self.id)

class VContainer(Element):
    """ Container class
    TODO: Make class a list, with automatic vnode addition/deletion
          when adding/retrieving items
    """
    def __init__(self, *args):
        Element.__init__(self, 'vcontainer')
        self.elements = []
        for e in args:
            if isinstance(e, dom.Element):
                self.elements.append(e)

    def append(self, e):
        self.appendChild(Html().vnode(e))
        
