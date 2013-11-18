import os
import shutil

from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins.configurator.api import ClassConfigEditor
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from backend import FMBackend, Item


@plugin
class FileManagerConfigEditor (ClassConfigEditor):
    title = _('File Manager')
    icon = 'folder-open'

    def init(self):
        self.append(self.ui.inflate('fm:config'))


@plugin
class FileManager (SectionPlugin):
    default_classconfig = {'root': '/'}
    classconfig_editor = FileManagerConfigEditor
    classconfig_root = True

    def init(self):
        self.title = _('File Manager')
        self.category = _('Tools')
        self.icon = 'folder-open'

        self.backend = FMBackend().get()

        self.append(self.ui.inflate('fm:main'))
        self.controller = Controller()

        def post_item_bind(object, collection, item, ui):
            ui.find('name').on('click', self.on_item_click, object, item)
            ui.find('edit').on('click', self.edit, item.fullpath)
        self.find('items').post_item_bind = post_item_bind

        def post_bc_bind(object, collection, item, ui):
            ui.find('name').on('click', self.on_bc_click, object, item)
        self.find('breadcrumbs').post_item_bind = post_bc_bind

        self.clipboard = []
        self.tabs = self.find('tabs')

    def on_first_page_load(self):
        self.controller.new_tab(self.classconfig['root'])
        self.binder = Binder(self.controller, self.find('filemanager')).autodiscover().populate()
        self.binder_c = Binder(self, self.find('bind-clipboard')).autodiscover().populate()


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
        try:
            open(os.path.join(self.controller.tabs[self.tabs.active].path, 'new file'), 'w').close()
        except OSError, e:
            self.context.notify('error', str(e))
        self.refresh()

    def upload(self, name, file):
        try:
            open(os.path.join(self.controller.tabs[self.tabs.active].path, name), 'w').write(file.read())
        except OSError, e:
            self.context.notify('error', str(e))
        self.refresh()

    @on('new-dir', 'click')
    def on_new_directory(self):
        path = os.path.join(self.controller.tabs[self.tabs.active].path, 'new directory')
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except OSError, e:
                self.context.notify('error', str(e))
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
        self.backend.remove(self._get_checked(), self.refresh)

    @on('paste', 'click')
    def on_paste(self):
        tab = self.controller.tabs[self.tabs.active]
        for_move = []
        for_copy = []
        for i in self.clipboard:
            if i.action == 'cut':
                for_move.append(i)
            else:
                for_copy.append(i)

        try:
            if for_move:
                self.backend.move(for_move, tab.path, self.refresh)
            if for_copy:
                self.backend.copy(for_copy, tab.path, self.refresh)
            self.clipboard = []
        except Exception as e:
            self.context.notify('error', str(e))
        self.refresh_clipboard()

    @on('select-all', 'click')
    def on_select_all(self):
        self.binder.update()
        tab = self.controller.tabs[self.tabs.active]
        for item in tab.items:
            item.checked = True
        self.binder.populate()
        self.context.notify('info', _('Selected %i items') % len(tab.items)) 

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

            if self.find('chmod-recursive').value:
                cmd = 'chown -Rv "%s:%s" "%s"; chmod -Rv %o "%s"' % (
                    self.item.owner, self.item.group,
                    self.item.fullpath,
                    self.item.mode,
                    self.item.fullpath,
                )
                self.context.launch('terminal', command=cmd)

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
    @url('/ajenti:fm-upload')
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
        for item in os.listdir(unicode(self.path)):
            itempath = os.path.join(self.path, item)
            if os.path.exists(itempath):
                self.items.append(Item(itempath))
        self.items = sorted(self.items, key=lambda x: (not x.isdir, x.name))

        self.breadcrumbs = []
        p = path
        while len(p) > 1:
            p = os.path.split(p)[0]
            self.breadcrumbs.insert(0, Breadcrumb(p))


class Breadcrumb (object):
    def __init__(self, path):
        self.name = os.path.split(path)[1]
        self.path = path
        if self.path == '/':
            self.name = '/'
