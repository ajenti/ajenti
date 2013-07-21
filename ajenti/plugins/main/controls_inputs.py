import os

from ajenti.api import *
from ajenti.ui import p, UIElement, on


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


@p('active', type=int)
@p('length', type=int)
@plugin
class Paging (UIElement):
    typeid = 'paging'


@p('value', default='', bindtypes=[str, unicode, int])
@p('directory', default=False, type=bool)
@p('type', default='text')
@plugin
class Pathbox (UIElement):
    typeid = 'pathbox'

    def init(self, *args, **kwargs):
        if self.directory:
            self.dialog = self.ui.create('opendirdialog')
        else:
            self.dialog = self.ui.create('openfiledialog')
        self.append(self.dialog)
        self.dialog.id = 'dialog'
        self.dialog.visible = False

    def on_start(self):
        self.find('dialog').navigate(os.path.split(self.value or '')[0] or '/')
        self.find('dialog').visible = True

    @on('dialog', 'select')
    def on_select(self, path=None):
        self.find('dialog').visible = False
        if path:
            self.value = path
