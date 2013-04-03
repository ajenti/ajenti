import os

from ajenti.api import *
from ajenti.plugins import *
from ajenti.ui import *


@p('buttons', default=[{'text':'OK', 'id':'ok'}], type=eval)
@plugin
class Dialog (UIElement):
    typeid = 'dialog'


@p('text', default='Input value:', type=unicode)
@p('value', default='', bindtypes=[str, unicode], type=unicode)
@plugin
class InputDialog (UIElement):
    typeid = 'inputdialog'

    def on_button(self, button):
        if button == 'ok':
            self.reverse_event('submit', {'value': self.value})
        self.visible = False


@p('_files', default=[], type=list)
@p('_dirs', default=[], type=list)
@p('path', default='/', type=unicode)
@plugin
class OpenFileDialog (UIElement):
    typeid = 'openfiledialog'

    def init(self):
        self.on('item-click', self.on_item_click)
        self.refresh()

    def on_item_click(self, item):
        path = os.path.abspath(os.path.join(self.path, item))
        if os.path.isdir(path):
            self.path = path
            self.refresh()
        else:
            self.reverse_event('select', {'path': path})

    def on_button(self, button=None):
        self.reverse_event('select', {'path': None})

    def refresh(self):
        self._dirs = []
        self._files = []
        if len(self.path) > 1:
            self._dirs.append('..')
        for item in sorted(os.listdir(self.path)):
            if os.path.isdir(os.path.join(self.path, item)):
                self._dirs.append(item)
            else:
                self._files.append(item)


@p('_dirs', default=[], type=list)
@p('path', default='/', type=unicode)
@plugin
class OpenDirDialog (UIElement):
    typeid = 'opendirdialog'

    def init(self):
        self.on('item-click', self.on_item_click)
        self.refresh()

    def on_item_click(self, item):
        self.path = os.path.abspath(os.path.join(self.path, item))
        self.refresh()

    def on_button(self, button=None):
        if button == 'select':
            self.reverse_event('select', {'path': self.path})
        else:
            self.reverse_event('select', {'path': None})

    def refresh(self):
        self._dirs = []
        if len(self.path) > 1:
            self._dirs.append('..')
        for item in sorted(os.listdir(self.path)):
            if os.path.isdir(os.path.join(self.path, item)):
                self._dirs.append(item)


@p('_dirs', default=[], type=list)
@p('path', default='/', type=unicode)
@plugin
class SaveFileDialog (UIElement):
    typeid = 'savefiledialog'

    def init(self):
        self.on('item-click', self.on_item_click)
        self.refresh()

    def on_item_click(self, item):
        path = os.path.abspath(os.path.join(self.path, item))
        if os.path.isdir(path):
            self.path = path
            self.refresh()
        else:
            self.reverse_event('select', {'path': path})

    def on_button(self, button=None):
        self.reverse_event('select', {'path': None})

    def refresh(self):
        self._dirs = []
        self._files = []
        if len(self.path) > 1:
            self._dirs.append('..')
        for item in sorted(os.listdir(self.path)):
            if os.path.isdir(os.path.join(self.path, item)):
                self._dirs.append(item)
