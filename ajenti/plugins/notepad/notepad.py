import mimetypes
import os

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin, intent
from ajenti.ui import on


@plugin
class Notepad (SectionPlugin):
    default_classconfig = {
        'bookmarks': []
    }
    SIZE_LIMIT = 1024 * 1024 * 5

    def init(self):
        self.title = _('Notepad')
        self.icon = 'edit'
        self.category = _('Tools')

        self.append(self.ui.inflate('notepad:main'))

        self.editor = self.find('editor')
        self.list = self.find('list')
        self.opendialog = self.find('opendialog')
        self.savedialog = self.find('savedialog')

        self.controller = Controller()

        self.selected = None

    def on_first_page_load(self):
        id = None
        if self.classconfig['bookmarks']:
            for path in self.classconfig['bookmarks']:
                if path:
                    id = self.controller.open(path)
        if id:
            self.select(id)
        else:
            self.on_new()

    def select(self, id):
        if self.selected in self.controller.files:
            self.controller.files[self.selected]['content'] = self.editor.value
        self.selected = id
        self.editor.value = self.controller.files[id]['content']
        self.editor.mode = self.controller.files[id]['mime']
        self.list.empty()
        for id, file in self.controller.files.iteritems():
            item = self.ui.inflate('notepad:listitem')
            item.find('name').text = file['path'] or _('Untitled %i') % id

            item.find('close').on('click', self.on_close, id)
            item.find('close').visible = len(self.controller.files.keys()) > 1
            item.on('click', self.select, id)

            if file['path'] in self.classconfig['bookmarks']:
                item.find('icon').icon = 'tag'
            self.list.append(item)

    @on('new-button', 'click')
    def on_new(self):
        self.select(self.controller.new())

    @on('open-button', 'click')
    def on_open(self):
        self.opendialog.visible = True

    @on('save-button', 'click')
    def on_save(self):
        path = self.controller.files[self.selected]['path']
        if not path:
            self.on_save_as()
        else:
            self.on_save_dialog_select(path)

    @on('save-as-button', 'click')
    def on_save_as(self):
        self.savedialog.visible = True

    @intent('notepad')
    @on('opendialog', 'select')
    def on_open_dialog_select(self, path=None):
        self.opendialog.visible = False
        if path:
            if os.stat(path).st_size > self.SIZE_LIMIT:
                self.context.notify('error', 'File is too big')
                return
            self.select(self.controller.open(path))
            self.activate()

    @on('savedialog', 'select')
    def on_save_dialog_select(self, path):
        self.savedialog.visible = False
        if path:
            self.select(self.selected)
            self.controller.save(self.selected, path)
            self.select(self.selected)
            self.context.notify('info', _('Saved'))

    def on_close(self, id):
        if self.controller.files[id]['path'] in self.classconfig['bookmarks']:
            self.classconfig['bookmarks'].remove(self.controller.files[id]['path'])
            self.save_classconfig()
        self.controller.close(id)
        self.select(self.controller.files.keys()[0])

    @on('bookmark-button', 'click')
    def on_bookmark(self):
        if not self.controller.files[self.selected]['path'] in self.classconfig['bookmarks']:
            self.classconfig['bookmarks'].append(self.controller.files[self.selected]['path'])
            self.save_classconfig()
        self.select(self.selected)


class Controller (object):
    def __init__(self):
        self.files = {}
        self._id = 0

    def new(self):
        id = self._id
        self._id += 1
        self.files[id] = {
            'id': id,
            'path': None,
            'content': '',
            'mime': None
        }
        return id

    def open(self, path):
        id = self.new()
        self.files[id]['path'] = path
        try:
            self.files[id]['content'] = open(path).read()
        except IOError:
            self.files[id]['content'] = ''
        self.files[id]['mime'] = mimetypes.guess_type(path, strict=False)[0]
        return id

    def save(self, id, path=None):
        path = path or self.files[id]['path']
        self.files[id]['path'] = path
        open(path, 'w').write(self.files[id]['content'])

    def close(self, id):
        del self.files[id]
