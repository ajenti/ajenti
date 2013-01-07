from ajenti.api import *
from ajenti.ui import p, UIElement


@p('text', default='', bindtypes=[str, unicode, int, float])
@p('style', default='')
@plugin
class Label (UIElement):
    typeid = 'label'


@p('text', default='', bindtypes=[str, unicode, int])
@p('style', default='')
@plugin
class Tooltip (UIElement):
    typeid = 'tooltip'


@p('icon', default=None, bindtypes=[str, unicode])
@p('style', default='normal')
@plugin
class Icon (UIElement):
    typeid = 'icon'


@p('text', default='', bindtypes=[str, unicode])
@p('icon', default=None)
@p('style', default='normal')
@p('warning', default=None)
@plugin
class Button (UIElement):
    typeid = 'button'


@p('width', default=None)
@p('value', default=0, type=float, bindtypes=[float])
@plugin
class ProgressBar (UIElement):
    typeid = 'progressbar'
