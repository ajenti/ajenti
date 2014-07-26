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
            'cancel': {'text': _('Cancel'), 'id': 'cancel'},
        }
        new_buttons = []
        for button in self.buttons:
            if isinstance(button, basestring) and button in presets:
                new_buttons.append(presets[button])
            else:
                new_buttons.append(button)
        self.buttons = new_buttons


@p('text', default='Input value:', type=unicode)
@p('value', default='', bindtypes=[str, unicode], type=unicode)
@plugin
class InputDialog (UIElement):
    typeid = 'inputdialog'

    def init(self):
        self.append(self.ui.inflate('main:input-dialog'))
        self.find('text').text = self.text

    def on_button(self, button):
        self.value = self.find('input').value
        if button == 'ok':
            self.reverse_event('submit', {'value': self.value})
        else:
            self.reverse_event('cancel', {})
        self.visible = False


class BaseFileDialog (object):
    shows_files = True
    layout = 'main:file-dialog'

    def navigate(self, path):
        self.path = path
        self.verify_path()
        self.refresh()

    def verify_path(self):
        if not self.path.startswith(self.root) or not os.path.isdir(self.path):
            self.path = self.root

    def show(self):
        self.visible = True
        self.refresh()

    def refresh(self):
        self.empty()
        self.append(self.ui.inflate(self.layout))
        list = self.find('list')
        _dirs = []
        if len(self.path) > 1:
            _dirs.append('..')

        if not os.path.exists(self.path):
            self.context.notify('error', _('The directory does not exist anymore'))
        else:
            _dirs += sorted(os.listdir(unicode(self.path)))

        for item in _dirs:
            isdir = os.path.isdir(os.path.join(self.path, item))
            if not self.shows_files and not isdir:
                continue
            itemui = self.ui.create('listitem', children=[
                self.ui.create('hc', children=[
                    self.ui.create('icon', icon='folder-open' if isdir else 'file'),
                    self.ui.create('label', text=item),
                ])
            ])
            itemui.on('click', self.on_item_click, item)
            list.append(itemui)


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


@p('path', default='/', type=unicode)
@p('root', default='/', type=unicode)
@plugin
class OpenDirDialog (UIElement, BaseFileDialog):
    typeid = 'opendirdialog'
    shows_files = False

    def init(self):
        self.verify_path()
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


@p('path', default='/', type=unicode)
@p('root', default='/', type=unicode)
@plugin
class SaveFileDialog (UIElement, BaseFileDialog):
    typeid = 'savefiledialog'
    shows_files = False
    layout = 'main:file-dialog-save'

    def init(self):
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
