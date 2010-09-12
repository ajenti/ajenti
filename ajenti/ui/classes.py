import random
import base64
from lxml import etree 

class Element(etree.ElementBase):
    """ Generate XML element

    @tag - element name
    *args - any number of dictionaries {'attribute':'value'}
    **kwargs - any number of keyword arguments attribute="value"
    """
    def __init__(self, tag, *args, **kwargs):
        etree.ElementBase.__init__(self)
        self.tag = tag
        self.set('id', str(random.randint(1,9000*9000)))
        for k in args:
            self.append(k)
        for k in kwargs:
            self[k] = kwargs[k]
    
    def __setitem__(self, idx, val):
        self.set(idx, str(val))
        
    def __getitem__(self, idx):
        return self.get(idx)
    
        
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

    """    @staticmethod
    def VContainer(*args, **kwargs):
        class VContainer(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'vcontainer', **kwargs)
                for e in args:
                    self.vnode(e)

            def vnode(self, e):
                vn = UI.vnode(e)
                vn['spacing'] = self['spacing']
                self.append(vn)

        return VContainer(*args, **kwargs)
    @staticmethod
    def HContainer(*args, **kwargs):
        class HContainer(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'hcontainer', **kwargs)
                for e in args:
                    self.hnode(e)

            def hnode(self, e):
                hn = UI.hnode(e)
                hn['spacing'] = self['spacing']
                self.append(hn)

        return HContainer(*args, **kwargs)
"""
    @staticmethod
    def Text(text):
        return Element('span', {'py:content':"'%s'"%text, 'py:strip':""})

    @staticmethod
    def LayoutTable(*args, **kwargs):
        class LayoutTable(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'layouttable', **kwargs)
                for e in args:
                    self.append(e)

        return LayoutTable(*args, **kwargs)

    @staticmethod
    def LayoutTableRow(*args, **kwargs):
        class LayoutTableRow(Element):
            def __init__(self, *args):
                Element.__init__(self, 'layouttablerow', **kwargs)
                for e in args:
                    if e.tag == 'layouttablecell':
                        self.append(e)
                    else:
                        c = UI.LayoutTableCell(e)
                        c['spacing'] = self['spacing']
                        self.append(c)

        return LayoutTableRow(*args, **kwargs)

    @staticmethod
    def DataTable(*args, **kwargs):
        class DataTable(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'datatable', **kwargs)
                for e in args:
                    self.append(e)

        return DataTable(*args, **kwargs)

    @staticmethod
    def DataTableRow(*args, **kwargs):
        class DataTableRow(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'datatablerow', **kwargs)
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
                Element.__init__(self, 'tabcontrol', **kwargs)
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
