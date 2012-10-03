import os
import re
import mimetypes

import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder
from ajenti.users import UserManager

from reconfigure.ext.nginx import NginxConfig


@plugin
class Notepad (SectionPlugin): 
    def init(self):
        self.title = 'Notepad'
        self.append(self.ui.inflate('notepad:main'))

        self.editor = self.find('editor')
        self.list = self.find('list')
        self.opendialog = self.find('opendialog')
        self.opendialog.on('button', self.on_open_dialog)
        self.opendialog.on('select', self.on_file_select)

        self.controller = Controller()

        self.find('new-button').on('click', self.on_new)
        self.find('open-button').on('click', self.on_open)

        self.selected = None
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
            item.find('name').text = file['path'] or 'Untitled %i' % id
            item.on('click', self.select, id)
            self.list.append(item)
        self.publish()

    def on_new(self):
        self.select(self.controller.new())

    def on_open(self):
        self.opendialog.visible = True
        self.publish()

    def on_file_select(self, path):
        self.opendialog.visible = False
        self.select(self.controller.open(path))

    def on_open_dialog(self, button):
        self.opendialog.visible = False        
        self.publish()


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
        self.files[id]['content'] = open(path).read()
        self.files[id]['mime'] = mimetypes.guess_type(path, strict=False)[0]
        return id
