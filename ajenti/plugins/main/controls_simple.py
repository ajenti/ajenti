from ajenti.api import *
from ajenti.ui import p, UIElement


@p('text', default='', bindtypes=[str, unicode, int])
@plugin
class Label (UIElement):
    typeid = 'label'


@p('icon', default=None, bindtypes=[str, unicode])
@p('style', default='normal')
@plugin
class Icon (UIElement):
    typeid = 'icon'


@p('text', default='', bindtypes=[str, unicode])
@p('icon', default=None)
@p('style', default='normal')
@plugin
class Button (UIElement):
    typeid = 'button'


@p('width', default=None)
@p('value', default=0, type=float, bindtypes=[float])
@plugin
class ProgressBar (UIElement):
    typeid = 'progressbar'
