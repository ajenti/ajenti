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
@plugin
class Table (UIElement):
    typeid = 'dt'


@p('width', default=None)
@plugin
class TableCell (UIElement):
    typeid = 'dtd'


@p('text', default='', bindtypes=[str, unicode])
@p('width', default=None)
@plugin
class TableHeader (UIElement):
    typeid = 'dth'


@p('title', default='', bindtypes=[str, unicode])
@plugin
class Tab (UIElement):
    typeid = 'tab'


@p('active', default=0)
@plugin
class Tabs (UIElement):
    typeid = 'tabs'
