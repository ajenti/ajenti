from ajenti.api import *
from ajenti.ui import p, UIElement


@p('text', default='')
@plugin
class Label (UIElement):
	typeid = 'label'


@p('text', default='')
@p('style', default='normal')
@plugin
class Button (UIElement):
	typeid = 'button'	


@plugin
class Form (UIElement):
	typeid = 'form'


@p('value', default='')
@plugin
class TextBox (UIElement):
	typeid = 'textbox'	

