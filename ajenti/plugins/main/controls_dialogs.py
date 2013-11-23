import os

from ajenti.api import *
from ajenti.plugins import *
from ajenti.ui import *


@p('buttons', default=['ok'], type=eval)
@plugin
class Dialog (UIElement):
    typeid = 'dialog'

    def init(self):
        presets = {
            'ok': {'text': 'OK', 'id': 'ok'},
            'cancel': {'text': 'Cancel', 'id': 'cancel'},
        }
        new_buttons = []
        for button in self.buttons:
            if type(button) == str and button in presets:
                new_buttons.append(presets[button])
            else:
                new_buttons.append(button)
        self.buttons = new_buttons


@p('text', default='Input value:', type=unicode)
@p('value', default='', bindtypes=[str, unicode], type=unicode)
@plugin
class InputDialog (UIElement):
    typeid = 'inputdialog'

    def on_button(self, button):
        if button == 'ok':
            self.reverse_event('submit', {'value': self.value})
        else:
            self.reverse_event('cancel', {})
        self.visible = False


class BaseFileDialog (object):
    def navigate(self, path):
        self.path = path
        self.verify_path()
        self.refresh()

    def verify_path(self):
        if not self.path.startswith(self.root):
            self.path = self.root

    def refresh(self):
        pass


@p('_files', default=[], type=list)
@p('_dirs', default=[], type=list)
@p('path', default='/', type=unicode)
@p('root', default='/', type=unicode)
@plugin
class OpenFileDialog (UIElement, BaseFileDialog):
    typeid = 'openfiledialog'

    def init(self):
        self.verify_path()
        self.refresh()

    def on_item_click(self, item):
        path = os.path.abspath(os.path.join(self.path, item))
        if os.path.isdir(path):
            self.navigate(path)
        else:
            self.reverse_event('select', {'path': path})

    def on_button(self, button=None):
        self.reverse_event('select', {'path': None})

    def refresh(self):
        self._dirs = []
        self._files = []
        if len(self.path) > 1:
            self._dirs.append('..')
        for item in sorted(os.listdir(unicode(self.path))):
            if os.path.isdir(os.path.join(self.path, item)):
                self._dirs.append(item)
            else:
                self._files.append(item)


@p('_dirs', default=[], type=list)
@p('path', default='/', type=unicode)
@p('root', default='/', type=unicode)
@plugin
class OpenDirDialog (UIElement, BaseFileDialog):
    typeid = 'opendirdialog'

    def init(self):
        self.verify_path()
        self.on('item-click', self.on_item_click)
        self.refresh()

    def on_item_click(self, item):
        path = os.path.abspath(os.path.join(self.path, item))
        if os.path.exists(path):
            self.navigate(path)

    def on_button(self, button=None):
        if button == 'select':
            self.reverse_event('select', {'path': self.path})
        else:
            self.reverse_event('select', {'path': None})

    def refresh(self):
        self._dirs = []
        if len(self.path) > 1:
            self._dirs.append('..')
        for item in sorted(os.listdir(unicode(self.path))):
            if os.path.isdir(os.path.join(self.path, item)):
                self._dirs.append(item)


@p('_dirs', default=[], type=list)
@p('path', default='/', type=unicode)
@p('root', default='/', type=unicode)
@plugin
class SaveFileDialog (UIElement, BaseFileDialog):
    typeid = 'savefiledialog'

    def init(self):
        self.on('item-click', self.on_item_click)
        self.refresh()

    def on_item_click(self, item):
        path = os.path.abspath(os.path.join(self.path, item))
        if os.path.isdir(path):
            self.navigate(path)
        else:
            self.reverse_event('select', {'path': path})

    def navigate(self, path):
        self.path = path
        self.verify_path()
        self.refresh()

    def on_button(self, button=None):
        self.reverse_event('select', {'path': None})

    def refresh(self):
        self._dirs = []
        self._files = []
        if len(self.path) > 1:
            self._dirs.append('..')
        for item in sorted(os.listdir(unicode(self.path))):
            if os.path.isdir(os.path.join(self.path, item)):
                self._dirs.append(item)
