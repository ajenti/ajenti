import random
import base64
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
    def CustomHTML(*args, **kwargs):
        class CustomHTML(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'customhtml', [], **kwargs)
                self.elements = []
                for e in args:
                    self['html'] = base64.b64encode(str(e))

        return CustomHTML(*args, **kwargs)

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
                vn = UI.vnode(e)
                vn['spacing'] = self['spacing']
                self.appendChild(vn)

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
                hn = UI.hnode(e)
                hn['spacing'] = self['spacing']
                self.appendChild(hn)

        return HContainer(*args, **kwargs)

    @staticmethod
    def Text(text):
        return Element('span', {'py:content':"'%s'"%text, 'py:strip':""})

    @staticmethod
    def LayoutTable(*args, **kwargs):
        class LayoutTable(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'layouttable', [], **kwargs)
                self.elements = []
                for e in args:
                    if isinstance(e, dom.Element):
                        self.appendChild(e)

        return LayoutTable(*args, **kwargs)

    @staticmethod
    def LayoutTableRow(*args, **kwargs):
        class LayoutTableRow(Element):
            def __init__(self, *args):
                Element.__init__(self, 'layouttablerow', [], **kwargs)
                self.elements = []
                for e in args:
                    if isinstance(e, dom.Element):
                        if e.tagName == 'layouttablecell':
                            self.appendChild(e)
                        else:
                            c = UI.LayoutTableCell(e)
                            c['spacing'] = self['spacing']
                            self.appendChild(c)

        return LayoutTableRow(*args, **kwargs)

    @staticmethod
    def DataTable(*args, **kwargs):
        class DataTable(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'datatable', [], **kwargs)
                self.elements = []
                for e in args:
                    if isinstance(e, dom.Element):
                        self.appendChild(e)

        return DataTable(*args, **kwargs)

    @staticmethod
    def DataTableRow(*args, **kwargs):
        class DataTableRow(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'datatablerow', [], **kwargs)
                self.elements = []
                for e in args:
                    if isinstance(e, dom.Element):
                        if e.tagName == 'datatablecell':
                            self.appendChild(e)
                        else:
                            self.appendChild(UI.DataTableCell(e))

        return DataTableRow(*args, **kwargs)

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

    @staticmethod
    def TabControl(*args, **kwargs):
        class TabControl(Element):
            vnt = None
            vnb = None
            tc = 0

            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'tabcontrol', [], **kwargs)
                self.elements = []
                self.vnt = UI.TabHeaderNode(id=self['id'])
                self.vnb = UI.VNode()
                self.appendChild(self.vnt)
                self.appendChild(self.vnb)

            def add(self, name, content):
                self.vnt.appendChild(UI.TabHeader(text=name, pid=self['id'], id=str(self.tc)))
                self.vnb.appendChild(UI.TabBody(content, pid=self['id'], id=str(self.tc)))
                self.tc += 1

        return TabControl(*args, **kwargs)


class TreeManager(object):
    """ Processes treenode click events and stores the nodes'
    collapsed/expanded states.
    You should keep the TreeManager inside the session,
    call node_click() on each 'click' event, and apply() to the tree
    object before rendering it.
    """
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
        pass

    def apply(self, tree):
        tree['expanded'] = tree['id'] in self.states;

        for n in tree.childNodes:
            if n.tagName == 'treecontainer':
                self.apply(n)
        pass
