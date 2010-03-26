import random
import xml.dom.minidom as dom


class Element(dom.Element):
    """ Generate XML element

    @tag - element name
    *args - any number of dictionaries {'attribute':'value'}
    **kwargs - any number of keyword arguments attribute="value"
    """
    def __init__(self, tag, *args, **kwargs):
        dom.Element.__init__(self, tag)
        self.setAttribute('id', str(random.randint(1,9000*9000)))
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


class UI(object):
    """ Automatically generate XML tags by calling name

    >>> m = UI.Meta(encoding="ru")
    >>> m.toxml()
    '<meta encoding="ru"/>'
    >>>
    """
    class __metaclass__(type):
        def __getattr__(cls, name):
            return lambda *args, **kw: Element(name.lower(), *args, **kw)

    @staticmethod
    def gen(name, *args, **kwargs):
        """ Generate XML tags by name, if name will violate Pyhton syntax

        >>> xi = UI.gen('xml:include', href="some.xml")
        >>> xi.toxml()
        '<xml:include href="some.xml"/>'
        >>>
        """
        return Element(name.lower(), *args, **kwargs)

    @staticmethod
    def VContainer(*args, **kwargs):
        class VContainer(Element):
            """ Container class
            To maintain same syntax with XML Templates - we should use vnode()
            """
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'vcontainer', [], **kwargs)
                self.elements = []
                for e in args:
                    if isinstance(e, dom.Element):
                        self.vnode(e)

            def vnode(self, e):
                self.appendChild(UI.vnode(e))

        return VContainer(*args, **kwargs)

    @staticmethod
    def HContainer(*args, **kwargs):
        class HContainer(Element):
            """ Container class
            To maintain same syntax with XML Templates - we should use hnode()
            """
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'hcontainer', [], **kwargs)
                self.elements = []
                for e in args:
                    if isinstance(e, dom.Element):
                        self.hnode(e)

            def hnode(self, e):
                self.appendChild(UI.hnode(e))

        return HContainer(*args, **kwargs)

    @staticmethod
    def Text(text):
        return Element('span', {'py:content':"'%s'"%text, 'py:strip':""})

    @staticmethod
    def Option(text='option', **kw):
        el = Element('option', **kw)
        el.appendChild(UI.Text(text))
        return el

    @staticmethod
    def LayoutTable(*args):
        class LayoutTable(Element):
            def __init__(self, *args):
                Element.__init__(self, 'layouttable')
                self.elements = []
                for e in args:
                    if isinstance(e, dom.Element):
                        self.appendChild(e)

        return LayoutTable(*args)

    @staticmethod
    def LayoutTableRow(*args):
        class LayoutTableRow(Element):
            def __init__(self, *args):
                Element.__init__(self, 'layouttablerow')
                self.elements = []
                for e in args:
                    if isinstance(e, dom.Element):
                        if e.tagName == 'layouttablecell':
                            self.appendChild(e)
                        else:
                            self.appendChild(UI.LayoutTableCell(e))

        return LayoutTableRow(*args)

    @staticmethod
    def DataTable(*args):
        class DataTable(Element):
            def __init__(self, *args):
                Element.__init__(self, 'datatable')
                self.elements = []
                for e in args:
                    if isinstance(e, dom.Element):
                        self.appendChild(e)

        return DataTable(*args)

    @staticmethod
    def DataTableRow(*args, **kwargs):
        class DataTableRow(Element):
            def __init__(self, *args):
                Element.__init__(self, 'datatablerow', **kwargs)
                self.elements = []
                for e in args:
                    if isinstance(e, dom.Element):
                        if e.tagName == 'datatablecell':
                            self.appendChild(e)
                        else:
                            self.appendChild(UI.DataTableCell(e))

        return DataTableRow(*args)

    @staticmethod
    def TreeContainer(*args, **kwargs):
        class TreeContainer(Element):
            def __init__(self, *args):
                Element.__init__(self, 'treecontainer', **kwargs)
                self.elements = []
                for e in args:
                    if isinstance(e, dom.Element):
                        if e.tagName == 'treecontainer':
                            self.appendChild(e)
                        elif e.tagName == 'treecontainernode':
                            self.appendChild(e)
                        else:
                            self.appendChild(UI.TreeContainerNode(e))

        return TreeContainer(*args)


class TreeManager(object):
    states = None

    def __init__(self):
        self.reset()

    def reset(self):
        self.states = []

    def node_click(self, id):
        if id in self.states:
            self.states.remove(id)
        else:
            self.states.append(id)
        print self.states
        pass

    def apply(self, tree):
        tree['expanded'] = tree['id'] in self.states;

        for n in tree.childNodes:
            if n.tagName == 'treecontainer':
                self.apply(n)
        pass
