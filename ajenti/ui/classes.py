import random
import base64
from lxml import etree 


class Element(etree.ElementBase):
    def __init__(self, tag, *args, **kwargs):
        etree.ElementBase.__init__(self)
        self.tag = tag
        self.set('id', str(random.randint(1,9000*9000)))
        for k in args:
            self.append(k)
        for k in kwargs:
            self[k] = kwargs[k]
    
    def append(self, el):
        if el is not None:
            etree.ElementBase.append(self, el)
        return self
        
    def __setitem__(self, idx, val):
        self.set(idx, unicode(str(val)))
        
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
                Element.__init__(self, 'customhtml', **kwargs)
                for e in args:
                    self['html'] = base64.b64encode(str(e))

        return CustomHTML(*args, **kwargs)

    @staticmethod
    def ProgressBar(*args, **kwargs):
        class ProgressBar(Element):
            def __init__(self, value=0, max=1, width=1):
                Element.__init__(self, 'progressbar', **kwargs)
                self['right'] = width - int(value*width/max)
                self['left'] = int(value*width/max)
                
        return ProgressBar(*args, **kwargs)

    @staticmethod
    def LayoutTable(*args, **kwargs):
        class LayoutTable(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'layouttable', **kwargs)
                for e in args:
                    if isinstance(e, Element):
                        if e.tag == 'layouttablerow':
                            self.append(e)
                        else:
                            self.append(UI.LayoutTableRow(e))

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
                    if isinstance(e, Element):
                        if e.tag == 'datatablerow':
                            self.append(e)
                        else:
                            self.append(UI.DataTableCell(e))
                for e in args:
                    self.append(e)

        return DataTable(*args, **kwargs)

    @staticmethod
    def DataTableRow(*args, **kwargs):
        class DataTableRow(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'datatablerow', **kwargs)
                for e in args:
                    if isinstance(e, Element):
                        if e.tag == 'datatablecell':
                            self.append(e)
                        else:
                            self.append(UI.DataTableCell(e))

        return DataTableRow(*args, **kwargs)

    @staticmethod
    def TreeContainer(*args, **kwargs):
        class TreeContainer(Element):
            def __init__(self, *args):
                Element.__init__(self, 'treecontainer', **kwargs)
                for e in args:
                    if isinstance(e, Element):
                        if e.tag == 'treecontainer':
                            self.append(e)
                        elif e.tag == 'treecontainernode':
                            self.append(e)
                        else:
                            self.append(UI.TreeContainerNode(e))

        return TreeContainer(*args)

    @staticmethod
    def TabControl(*args, **kwargs):
        class TabControl(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'tabcontrol', **kwargs)
                self.vnt = UI.TabHeaderNode(id=self['id'])
                self.vnc = UI.Container()
                self.append(UI.VContainer(self.vnt, spacing=10))
                self.append(self.vnc)
                self.tc = 0

            def add(self, name, content):
                self.vnt.append(UI.TabHeader(text=name, pid=self['id'], id=str(self.tc)))
                self.vnc.append(UI.TabBody(content, pid=self['id'], id=str(self.tc)))
                self.tc += 1

        tc = TabControl(*args, **kwargs)
        return tc


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
        
    def apply(self, tree):
        try:
            tree['expanded'] = tree['id'] in self.states

            for n in tree.getchildren():
                if n.tag == 'treecontainer':
                    self.apply(n)
        except:
            pass
