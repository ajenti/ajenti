from ajenti.api import *
from ajenti.ui import p, UIElement


@p('text', default='', bindtypes=[str, unicode, int])
@plugin
class Label (UIElement):
	typeid = 'label'


@p('text', default='', bindtypes=[str, unicode])
@p('style', default='normal')
@plugin
class Button (UIElement):
	typeid = 'button'	


@p('value', default='', bindtypes=[str, unicode, int])
@p('type', default='text')
@plugin
class TextBox (UIElement):
	typeid = 'textbox'	


@p('text', default='', bindtypes=[bool])
@p('value', default=False)
@plugin
class CheckBox (UIElement):
	typeid = 'checkbox'	


@p('text', default='', bindtypes=[str, unicode])
@plugin
class FormLine (UIElement):
	typeid = 'formline'	


@p('text', default='', bindtypes=[str, unicode])
@plugin
class FormGroup (UIElement):
	typeid = 'formgroup'