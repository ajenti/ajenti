import gevent
import grp
import logging
import os
import pwd

from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins.configurator.api import ClassConfigEditor
from ajenti.plugins.main.api import SectionPlugin, intent
from ajenti.ui import on
from ajenti.ui.binder import Binder

from backend import FMBackend, Item, Unpacker


@plugin
class FileManagerConfigEditor (ClassConfigEditor):
    title = _('File Manager')
    icon = 'folder-open'

    def init(self):
        self.append(self.ui.inflate('fm:config'))


@plugin
class FileManager (SectionPlugin):
    default_classconfig = {'root': '/', 'start': '/'}
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
        self.new_tab()
        self.binder = Binder(self.controller, self.find('filemanager')).populate()
        self.binder_c = Binder(self, self.find('bind-clipboard')).populate()

    def on_page_load(self):
        self.refresh()

    def refresh_clipboard(self):
        self.binder_c.setup().populate()

    @on('tabs', 'switch')
    def on_tab_switch(self):
        if self.tabs.active == (len(self.controller.tabs) - 1):
            self.new_tab()
        self.refresh()

    @intent('fm:browse')
    def new_tab(self, path=None):
        dir = path or self.classconfig.get('start', None) or '/'
        if not dir.startswith(self.classconfig['root']):
            dir = self.classconfig['root']
        self.controller.new_tab(dir)
        if not self.active:
            self.activate()

    @on('close', 'click')
    def on_tab_close(self):
        if len(self.controller.tabs) > 2:
            self.controller.tabs.pop(self.tabs.active)
        self.tabs.active = 0
        self.refresh()

    @on('new-file', 'click')
    def on_new_file(self):
        destination = self.controller.tabs[self.tabs.active].path
        logging.info('[fm] new file in %s' % destination)
        path = os.path.join(destination, 'new file')
        try:
            open(path, 'w').close()
            self._chown_new(path)
        except OSError as e:
            self.context.notify('error', str(e))
        self.refresh()

    @on('new-dir', 'click')
    def on_new_directory(self):
        destination = self.controller.tabs[self.tabs.active].path
        logging.info('[fm] new directory in %s' % destination)
        path = os.path.join(destination, 'new directory')
        if not os.path.exists(path):
            try:
                os.mkdir(path)
                os.chmod(path, 0755)
                self._chown_new(path)
            except OSError as e:
                self.context.notify('error', str(e))
        self.refresh()

    def _chown_new(self, path):
        uid = self.classconfig.get('new_owner', 'root') or 'root'
        gid = self.classconfig.get('new_group', 'root') or 'root'
        try:
            uid = int(uid)
        except:
            uid = pwd.getpwnam(uid)[2]
        try:
            gid = int(gid)
        except:
            gid = grp.getgrnam(gid)[2]
        os.chown(path, uid, gid)

    def upload(self, name, file):
        destination = self.controller.tabs[self.tabs.active].path
        logging.info('[fm] uploading %s to %s' % (name, destination))
        try:
            output = open(os.path.join(destination, name), 'w')
            while True:
                data = file.read(1024 * 1024)
                if not data:
                    break
                gevent.sleep(0)
                output.write(data)
            output.close()
        except OSError as e:
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
        def callback(task):
            self.context.notify('info', _('Files deleted'))
            self.refresh()
        self.backend.remove(self._get_checked(), cb=callback)

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
                def callback(task):
                    self.context.notify('info', _('Files moved'))
                    self.refresh()
                self.backend.move(for_move, tab.path, callback)
            if for_copy:
                def callback(task):
                    self.context.notify('info', _('Files copied'))
                    self.refresh()
                self.backend.copy(for_copy, tab.path, callback)
            self.clipboard = []
        except Exception as e:
            self.context.notify('error', str(e))
        self.refresh_clipboard()

    @on('select-all', 'click')
    def on_select_all(self):
        self.binder.update()
        tab = self.controller.tabs[self.tabs.active]
        for item in tab.items:
            item.checked = not item.checked
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
        self.binder_d = Binder(self.item, self.find('dialog')).populate()

        # Unpack
        u = Unpacker.find(self.item.fullpath.lower())
        unpack_btn = self.find('dialog').find('unpack')
        unpack_btn.visible = u is not None

        def cb():
            self.context.notify('info', _('Unpacked'))
            self.refresh()

        def unpack():
            u.unpack(self.item.fullpath, cb=cb)
            logging.info('[fm] unpacking %s' % self.item.fullpath)

        unpack_btn.on('click', lambda: unpack())

        # Edit
        edit_btn = self.find('dialog').find('edit')
        if self.item.size > 1024 * 1024 * 5:
            edit_btn.visible = False

        def edit():
            self.context.launch('notepad', path=self.item.fullpath)

        edit_btn.on('click', lambda: edit())

    @on('dialog', 'button')
    def on_close_dialog(self, button):
        self.find('dialog').visible = False
        if button == 'save':
            self.binder_d.update()
            try:
                self.item.write()
            except Exception as e:
                self.context.notify('error', str(e))
            self.refresh()

            if self.find('chmod-recursive').value:
                cmd = 'chown -Rv "%s:%s" "%s"; chmod -Rv %o "%s"' % (
                    self.item.owner, self.item.group,
                    self.item.fullpath,
                    self.item.mode,
                    self.item.fullpath,
                )
                self.context.launch('terminal', command=cmd)

            logging.info('[fm] modifying %s: %o %s:%s' % (self.item.fullpath, self.item.mode, self.item.owner, self.item.group))

    def on_bc_click(self, tab, item):
        if not item.path.startswith(self.classconfig['root']):
            return
        tab.navigate(item.path)
        self.refresh()

    def refresh(self, _=None):
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
