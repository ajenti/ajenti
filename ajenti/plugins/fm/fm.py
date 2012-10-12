import os

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder
from ajenti.util import str_fsize


@plugin
class FileManager (SectionPlugin):
    def init(self):
        self.title = 'File manager'
        self.category = 'Tools'

        self.append(self.ui.inflate('fm:main'))
        self.controller = Controller()
        self.controller.new_tab()

        def post_item_bind(object, collection, item, ui):
            ui.find('name').on('click', self.on_item_click, object, item)

        self.find('items').post_item_bind = post_item_bind
        self.binder = Binder(self.controller, self.find('filemanager'))
        self.binder.autodiscover()
        self.binder.populate()

        self.tabs = self.find('tabs')
        self.tabs.on('switch', self.on_tab_switch)

    def on_tab_switch(self):
        if self.tabs.active == (len(self.controller.tabs) - 1):
            self.controller.new_tab()
        self.refresh()

    def on_item_click(self, tab, item):
        tab.navigate(os.path.join(tab.path, item.name))
        self.refresh()

    def refresh(self):
        self.binder.populate()
        self.publish()

class Controller (object):
    def __init__(self):
        self.tabs = []

    def new_tab(self):
        if len(self.tabs) > 1:
            self.tabs.pop(-1)
        self.tabs.append(Tab('/'))
        self.tabs.append(Tab(None))


class Tab (object):
    def __init__(self, path):
        if path:
            self.navigate(path)
        else:
            self.shortpath = '+'

    def navigate(self, path):
        self.path = path
        self.shortpath = os.path.split(path)[1] or '/'
        self.items = []
        for item in os.listdir(self.path):
            self.items.append(Item(os.path.join(self.path, item)))
        self.items = sorted(self.items, key=lambda x: (not x.isdir, x.name))


class Item (object):
    def __init__(self, path):
        self.path, self.name = os.path.split(path)
        self.isdir = os.path.isdir(path)
        self.icon = 'folder-close' if self.isdir else 'file'
        self.sizestr = '' if self.isdir else str_fsize(os.path.getsize(path))
