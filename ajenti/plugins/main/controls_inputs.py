from ajenti.api import *
from ajenti.ui import p, UIElement


@p('value', default='', bindtypes=[str, unicode, int])
@p('type', default='text')
@plugin
class TextBox (UIElement):
    typeid = 'textbox'


@p('value', default='', bindtypes=[str, unicode, int])
@plugin
class PasswordBox (UIElement):
    typeid = 'passwordbox'


@p('value', default='', bindtypes=[str, unicode])
@p('icon', default=None)
@p('placeholder', default=None)
@plugin
class Editable (UIElement):
    typeid = 'editable'


@p('text', default='')
@p('value', default=False, bindtypes=[bool])
@plugin
class CheckBox (UIElement):
    typeid = 'checkbox'


@p('labels', default=[], type=list)
@p('values', default=[], type=list)
@p('value', default='', bindtypes=[str, int, unicode])
@p('server', default=False, type=bool)
@plugin
class Dropdown (UIElement):
    typeid = 'dropdown'


@p('labels', default=[], type=list)
@p('values', default=[], type=list)
@p('separator', default=None, type=str)
@p('value', default='', bindtypes=[str, unicode])
@plugin
class Combobox (UIElement):
    typeid = 'combobox'


@p('target', type=str)
@plugin
class FileUpload (UIElement):
    typeid = 'fileupload'
