from ajenti.api import *
from ajenti.ui import p, UIElement


@p('text', default='', bindtypes=[str, unicode, int, float])
@plugin
class Label (UIElement):
    typeid = 'label'


@p('text', default='', bindtypes=[str, unicode, int])
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


@p('width', default=None)
@p('value', default=0, type=float, bindtypes=[int, float])
@plugin
class ProgressBar (UIElement):
    typeid = 'progressbar'
