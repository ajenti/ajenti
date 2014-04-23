from ajenti.api import *
from ajenti.ui import p, UIElement


@p('width', default=None)
@p('height', default=None)
@p('scroll', default=False, type=bool)
@plugin
class Box (UIElement):
    typeid = 'box'


@p('text', default='', bindtypes=[str, unicode])
@plugin
class FormLine (UIElement):
    typeid = 'formline'


@p('text', default='', bindtypes=[str, unicode])
@plugin
class FormGroup (UIElement):
    typeid = 'formgroup'


@p('expanded', default=False, type=bool, bindtypes=[bool])
@plugin
class Collapse (UIElement):
    typeid = 'collapse'


@p('expanded', default=False, type=bool, bindtypes=[bool])
@plugin
class CollapseRow (UIElement):
    typeid = 'collapserow'


@p('width', default='99%')
@p('emptytext', type=unicode, default=_('Empty'))
@p('filtering', type=bool, default=True)
@p('filterrow', type=unicode, default=_('Filter...'))
@p('filter', type=unicode, default='')
@p('addrow', type=unicode, default=None)
@plugin
class Table (UIElement):
    typeid = 'dt'


@p('sortable', default=True, type=bool)
@p('order', default='', type=str)
@plugin
class SortableTable (Table):
    typeid = 'sortabledt'


@p('header', default=False)
@plugin
class TableRow (UIElement):
    typeid = 'dtr'


@p('width', default=None)
@p('forcewidth', default=None)
@plugin
class TableCell (UIElement):
    typeid = 'dtd'


@p('text', default='', bindtypes=[str, unicode])
@p('width', default=None)
@plugin
class TableHeader (UIElement):
    typeid = 'dth'


@p('width', default='99%')
@plugin
class LayoutTable (UIElement):
    typeid = 'lt'


@p('width', default=None)
@plugin
class LayoutTableCell (UIElement):
    typeid = 'ltd'


@p('title', default='', bindtypes=[str, unicode])
@plugin
class Tab (UIElement):
    typeid = 'tab'


@p('active', type=int, default=0)
@plugin
class Tabs (UIElement):
    typeid = 'tabs'

    def init(self):
        self._active = 0
        self.refresh()

    #---

    def active_get(self):
        return getattr(self, '_active', 0)

    def active_set(self, active):
        self._active = active
        self.on_switch()

    active = property(active_get, active_set)

    #---

    def on_switch(self):
        self.children_changed = True  # force update
        self.refresh()

    def refresh(self):
        for i, child in enumerate(self.children):
            child.visible = int(self.active) == i
            if child.visible:
                child.broadcast('on_tab_shown')
