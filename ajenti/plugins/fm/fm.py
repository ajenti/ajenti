import os
import shutil
import stat
import pwd
import grp

from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins.configurator.api import ClassConfigEditor
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder
from ajenti.util import str_fsize


@plugin
class FileManagerConfigEditor (ClassConfigEditor):
    title = 'File Manager'
    icon = 'folder-open'

    def init(self):
        self.append(self.ui.inflate('fm:config'))


@plugin
class FileManager (SectionPlugin):
    default_classconfig = {'root': '/'}
    classconfig_editor = FileManagerConfigEditor
    classconfig_root = True

    def init(self):
        self.title = 'File Manager'
        self.category = 'Tools'
        self.icon = 'folder-open'

        self.append(self.ui.inflate('fm:main'))
        self.controller = Controller()
        self.controller.new_tab(self.classconfig['root'])

        def post_item_bind(object, collection, item, ui):
            ui.find('name').on('click', self.on_item_click, object, item)
            ui.find('edit').on('click', self.edit, item.fullpath)
        self.find('items').post_item_bind = post_item_bind

        def post_bc_bind(object, collection, item, ui):
            ui.find('name').on('click', self.on_bc_click, object, item)
        self.find('breadcrumbs').post_item_bind = post_bc_bind

        self.binder = Binder(self.controller, self.find('filemanager')).autodiscover().populate()
        self.clipboard = []
        self.binder_c = Binder(self, self.find('filemanager')).autodiscover().populate()
        self.tabs = self.find('tabs')

        self.find('dialog').buttons = [
            {'id': 'save', 'text': 'Save'},
            {'id': 'cancel', 'text': 'Cancel'},
        ]

    def refresh_clipboard(self):
        self.binder_c.reset().autodiscover().populate()

    @on('tabs', 'switch')
    def on_tab_switch(self):
        if self.tabs.active == (len(self.controller.tabs) - 1):
            self.controller.new_tab(self.classconfig['root'])
        self.refresh()

    @on('close', 'click')
    def on_tab_close(self):
        if len(self.controller.tabs) > 2:
            self.controller.tabs.pop(self.tabs.active)
        self.tabs.active = 0
        self.refresh()

    @on('new-file', 'click')
    def on_new_file(self):
        open(os.path.join(self.controller.tabs[self.tabs.active].path, 'new file'), 'w').close()
        self.refresh()

    def upload(self, name, file):
        open(os.path.join(self.controller.tabs[self.tabs.active].path, name), 'w').write(file.read())
        self.refresh()

    @on('new-dir', 'click')
    def on_new_directory(self):
        os.mkdir(os.path.join(self.controller.tabs[self.tabs.active].path, 'new directory'))
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

    @on('mass-delete', 'click')
    def on_delete(self):
        for i in self._get_checked():
            if os.path.isdir(i.fullpath):
                shutil.rmtree(i.fullpath)
            else:
                os.unlink(i.fullpath)
        self.refresh()

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
        path = os.path.join(tab.path, item.name)
        if not os.path.isdir(path):
            self.edit(path)
        if not path.startswith(self.classconfig['root']):
            return
        tab.navigate(path)
        self.refresh()

    def edit(self, path):
        self.find('dialog').visible = True
        self.item = Item(path)
        self.item.read()
        self.binder_d = Binder(self.item, self.find('dialog')).autodiscover().populate()

    @on('dialog', 'button')
    def on_close_dialog(self, button):
        self.find('dialog').visible = False
        if button == 'save':
            self.binder_d.update()
            self.item.write()
            self.refresh()

    def on_bc_click(self, tab, item):
        if not item.path.startswith(self.classconfig['root']):
            return
        tab.navigate(item.path)
        self.refresh()

    def refresh(self):
        for tab in self.controller.tabs:
            tab.refresh()
        self.binder.populate()


@plugin
class UploadReceiver (HttpPlugin):
    @url('/fm-upload')
    def handle_upload(self, context):
        file = context.query['file']
        context.session.endpoint.get_section(FileManager).upload(file.filename, file.file)
        context.respond_ok()
        return 'OK'


class Controller (object):
    def __init__(self):
        self.tabs = []

    def new_tab(self, path='/'):
        if len(self.tabs) > 1:
            self.tabs.pop(-1)
        self.tabs.append(Tab(path))
        self.tabs.append(Tab(None))


class Tab (object):
    def __init__(self, path):
        if path:
            self.navigate(path)
        else:
            self.shortpath = '+'
            self.path = None

    def refresh(self):
        if self.path:
            self.navigate(self.path)

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
    stat_bits = [
        stat.S_IRUSR,
        stat.S_IWUSR,
        stat.S_IXUSR,
        stat.S_IRGRP,
        stat.S_IWGRP,
        stat.S_IXGRP,
        stat.S_IROTH,
        stat.S_IWOTH,
        stat.S_IXOTH,
    ]

    def __init__(self, path):
        self.checked = False
        self.path, self.name = os.path.split(path)
        self.fullpath = path
        self.isdir = os.path.isdir(path)
        self.icon = 'folder-close' if self.isdir else 'file'
        self.sizestr = '' if self.isdir else str_fsize(os.path.getsize(path))

    def read(self):
        stat = os.stat(self.fullpath)
        self.owner = pwd.getpwuid(stat.st_uid)[0]
        self.group = grp.getgrgid(stat.st_gid)[0]
        self.mod_ur, self.mod_uw, self.mod_ux, \
            self.mod_gr, self.mod_gw, self.mod_gx, \
            self.mod_ar, self.mod_aw, self.mod_ax = [
                (stat.st_mode & Item.stat_bits[i] != 0)
                for i in range(0, 9)
            ]

    def write(self):
        mods = [self.mod_ur, self.mod_uw, self.mod_ux, \
            self.mod_gr, self.mod_gw, self.mod_gx, \
            self.mod_ar, self.mod_aw, self.mod_ax]
        chmod = sum(
                Item.stat_bits[i] * (1 if mods[i] else 0)
                for i in range(0, 9)
            )
        os.chmod(self.fullpath, chmod)
        os.chown(self.fullpath, pwd.getpwnam(self.owner)[2], grp.getgrnam(self.group)[2])
        os.rename(self.fullpath, os.path.join(self.path, self.name))


class Breadcrumb (object):
    def __init__(self, path):
        self.name = os.path.split(path)[1]
        self.path = path
        if self.path == '/':
            self.name = '/'
