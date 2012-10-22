import os

from ajenti.api import *
from ajenti.plugins import *
from ajenti.ui import *


@p('buttons', default=[{'text':'OK', 'id':'ok'}], type=eval)
@plugin
class Dialog (UIElement):
    typeid = 'dialog'


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
            self.publish()
        else:
            self.event('select', {'path': path})

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
            self.publish()
        else:
            self.event('select', {'path': path})

    def refresh(self):
        self._dirs = []
        self._files = []
        if len(self.path) > 1:
            self._dirs.append('..')
        for item in sorted(os.listdir(self.path)):
            if os.path.isdir(os.path.join(self.path, item)):
                self._dirs.append(item)
