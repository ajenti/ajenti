from ajenti.api import *
from ajenti.ui import p, UIElement


@p('text', default='')
@plugin
class Label (UIElement):
	id = 'label'


@p('text', default='')
@plugin
class Button (UIElement):
	id = 'button'	