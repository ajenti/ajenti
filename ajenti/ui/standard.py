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


@p('value', default='')
@plugin
class TextBox (UIElement):
	typeid = 'textbox'	


@p('text', default='')
@p('value', default=False)
@plugin
class CheckBox (UIElement):
	typeid = 'checkbox'	


@p('text', default='')
@plugin
class FormLine (UIElement):
	typeid = 'formline'	


@p('text', default='')
@plugin
class FormGroup (UIElement):
	typeid = 'formgroup'