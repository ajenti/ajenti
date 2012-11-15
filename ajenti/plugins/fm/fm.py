import os

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
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

        def post_bc_bind(object, collection, item, ui):
            ui.find('name').on('click', self.on_bc_click, object, item)
        self.find('breadcrumbs').post_item_bind = post_bc_bind

        self.binder = Binder(self.controller, self.find('filemanager')).autodiscover().populate()
        self.clipboard = []
        self.binder_c = Binder(self, self.find('filemanager')).autodiscover().populate()
        self.tabs = self.find('tabs')

    def refresh_clipboard(self):
        self.binder_c.reset().autodiscover().populate()

    @on('tabs', 'switch')
    def on_tab_switch(self):
        if self.tabs.active == (len(self.controller.tabs) - 1):
            self.controller.new_tab()
        self.refresh()

    @on('close', 'click')
    def on_tab_close(self):
        if len(self.controller.tabs) > 1:
            self.controller.tabs.pop(self.tabs.active)
        self.tabs.active = 0
        self.refresh()

    @on('mass-cut', 'click')
    def on_cut(self):
        l = self._get_checked()
        for i in l:
            i.action = 'cut'
        self.clipboard += l
        self.refresh_clipboard()

    @on('mass-copy', 'click')
    def on_copy(self):
        l = self._get_checked()
        for i in l:
            i.action = 'copy'
        self.clipboard += l
        self.refresh_clipboard()

    @on('paste', 'click')
    def on_paste(self):
        tab = self.controller.tabs[self.tabs.active]
        for i in self.clipboard:
            if i.action == 'cut':
                shutil.move(i.fullpath, tab.path)
            else:
                if os.path.isdir(i.fullpath):
                    shutil.copytree(i.fullpath, os.path.join(tab.path, i.name))
                else:
                    shutil.copy(i.fullpath, os.path.join(tab.path, i.name))
        self.clipboard = []
        self.refresh_clipboard()
        self.refresh()

    def _get_checked(self):
        self.binder.update()
        tab = self.controller.tabs[self.tabs.active]
        r = []
        for item in tab.items:
            if item.checked:
                r.append(item)
                item.checked = False
        self.refresh()
        return r

    @on('clear-clipboard', 'click')
    def on_clear_clipboard(self):
        self.clipboard = []
        self.refresh_clipboard()

    def on_item_click(self, tab, item):
        tab.navigate(os.path.join(tab.path, item.name))
        self.refresh()

    def on_bc_click(self, tab, item):
        tab.navigate(item.path)
        self.refresh()

    def refresh(self):
        self.binder.populate()


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
        if not os.path.isdir(path):
            return
        self.path = path
        self.shortpath = os.path.split(path)[1] or '/'
        self.items = []
        for item in os.listdir(self.path):
            self.items.append(Item(os.path.join(self.path, item)))
        self.items = sorted(self.items, key=lambda x: (not x.isdir, x.name))

        self.breadcrumbs = []
        p = path
        while len(p) > 1:
            p = os.path.split(p)[0]
            self.breadcrumbs.insert(0, Breadcrumb(p))


class Item (object):
    def __init__(self, path):
        self.checked = False
        self.path, self.name = os.path.split(path)
        self.fullpath = path
        self.isdir = os.path.isdir(path)
        self.icon = 'folder-close' if self.isdir else 'file'
        self.sizestr = '' if self.isdir else str_fsize(os.path.getsize(path))


class Breadcrumb (object):
    def __init__(self, path):
        self.name = os.path.split(path)[1]
        self.path = path
        if self.path == '/':
            self.name = '/'
