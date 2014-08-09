from ajenti.api import *
from ajenti.ui import p, UIElement


@p('text', default='', bindtypes=[str, unicode, int, float, long])
@p('escape', type=bool, default=True)
@plugin
class Label (UIElement):
    typeid = 'label'


@p('text', default='', bindtypes=[str, unicode, int, long])
@plugin
class Tooltip (UIElement):
    typeid = 'tooltip'


@p('icon', default=None, bindtypes=[str, unicode])
@plugin
class Icon (UIElement):
    typeid = 'icon'


@p('text', default='', bindtypes=[str, unicode])
@p('icon', default=None)
@p('warning', default=None)
@plugin
class Button (UIElement):
    typeid = 'button'


@p('text', default='', bindtypes=[str, unicode])
@p('icon', default=None)
@p('pressed', default=False, type=bool)
@plugin
class ToggleButton (UIElement):
    typeid = 'togglebutton'


@p('width', default=None)
@p('value', default=0, type=float, bindtypes=[int, float, long])
@plugin
class ProgressBar (UIElement):
    typeid = 'progressbar'
