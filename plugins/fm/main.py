# coding: utf-8
from ajenti.ui import *
from ajenti.api import *
from ajenti.plugins.core.api import *
from ajenti.utils import *
import os
from base64 import b64encode, b64decode
from stat import ST_UID, ST_GID, ST_MODE, ST_SIZE
import grp, pwd
import shutil
import threading
from acl import *


class FMPlugin(CategoryPlugin):
    text = 'File manager'
    icon = '/dl/fm/icon.png'
    folder = 'tools'

    def on_init(self):
        self._has_acls = shell_status('which getfacl')==0
        
    def on_session_start(self):
        self._root = self.app.get_config(self).dir
        self._tabs = []
        self._tab = 0
        self._clipboard = []
        self._cbs = None
        self._renaming = None
        self.add_tab()

    def get_ui(self):
        ui = self.app.inflate('fm:main')
        tc = UI.TabControl(active=self._tab)

        for tab in self._tabs:
            tc.add(tab, self.get_tab(tab))

        self._clipboard = sorted(self._clipboard)
        idx = 0
        for f in self._clipboard:
            ui.append('clipboard', UI.DataTableRow(
                UI.DataTableCell(
                    UI.Image(file='/dl/fm/'+
                        ('folder' if os.path.isdir(f) else 'file')
                        +'.png'),
                    UI.Label(text=f),
                ),
                UI.MiniButton(
                    text='Remove',
                    id='rmClipboard/%i'%idx
                ),
            ))
            idx += 1

        ui.append('main', tc)

        if self._renaming is not None:
            ui.append('main', UI.InputBox(
                text='New name',
                value=os.path.split(self._renaming)[1],
                id='dlgRename'
            ))

        if self._editing_acl is not None:
            dlg = self.app.inflate('fm:acl')
            ui.append('main', dlg)
            acls = get_acls(self._editing_acl)
            idx = 0
            for acl in acls:
                dlg.append('list', UI.DataTableRow(
                    UI.Editable(id='edAclSubject/%i'%idx, value=acl[0]),
                    UI.Editable(id='edAclPerm/%i'%idx, value=acl[1]),
                    UI.MiniButton(
                        text='Delete',
                        id='delAcl/%i'%idx
                    )
                ))
                idx += 1
            
        return ui

    def get_tab(self, tab):
        ui = self.app.inflate('fm:tab')

        tidx = self._tabs.index(tab)
        ui.find('paste').set('id', 'paste/%i'%tidx)
        ui.find('newfld').set('id', 'newfld/%i'%tidx)
        ui.find('close').set('id', 'close/%i'%tidx)

        # Generate breadcrumbs
        path = tab
        parts = path.split('/')
        while '' in parts:
            parts.remove('')
        parts.insert(0, '/')

        idx = 0
        for part in parts:
            ui.append('path', UI.ToolButton(
                text=part,
                id='goto/%i/%s' % (
                    tidx,
                    self.enc_file('/'.join(parts[:idx+1])),
                )
            ))
            idx += 1

        # File listing
        templist = os.listdir(path)
        lst = []

        for x in sorted(templist):
            if os.path.isdir(os.path.join(path, x)):
                lst.append(x)
        for x in sorted(templist):
            if not os.path.isdir(os.path.join(path, x)):
                lst.append(x)

        for f in lst:
            np = os.path.join(path, f)
            isdir = os.path.isdir(np)
            islink = os.path.islink(np)
            ismount = os.path.ismount(np)

            icon = 'file'
            if isdir: icon = 'folder'
            if islink: icon ='link'
            if ismount: icon = 'mount'

            try:
                stat = os.stat(np)
                mode = stat[ST_MODE]
                size = stat[ST_SIZE]
            except:
                continue

            try:
                user = pwd.getpwuid(stat[ST_UID])[0]
            except:
                user = str(stat[ST_UID])
            try:
                group = grp.getgrgid(stat[ST_GID])[0]
            except:
                group = str(stat[ST_GID])
            
            name = f
            if islink:
                name += ' → ' + os.path.realpath(np)
                
            row = UI.DataTableRow(
                UI.Checkbox(name='%i/%s' % (
                    tidx,
                    self.enc_file(np)
                )),
                UI.DataTableCell(
                    UI.Image(file='/dl/fm/%s.png'%icon),
                    UI.Label(text=name) if not isdir else
                    UI.LinkLabel(text=name, id='goto/%i/%s' % (
                        tidx,
                        self.enc_file(np)
                    )),
                    UI.LinkLabel(
                        text='↗',
                        id='gototab/%i/%s' % (
                            tidx,
                            self.enc_file(np)
                    )) if isdir else None,
                ),
                UI.Label(text=str_fsize(size)),
                UI.Label(text='%s:%s'%(user,group), monospace=True),
                UI.Label(text=self.mode_string(mode), monospace=True),
                UI.DataTableCell(
                    UI.MiniButton(
                        text='ACLs',
                        id='acls/%i/%s'%(
                            tidx,
                            self.enc_file(np)
                        ),
                    ) if self._has_acls else None,
                    UI.WarningMiniButton(
                        text='Delete',
                        msg='Delete %s'%np,
                        id='delete/%i/%s'%(
                            tidx,
                            self.enc_file(np)
                        ),
                    ),
                    hidden=True
                )
            )

            ui.append('list', row)
        return ui

    def enc_file(self, path):
        path = path.replace('//','/')
        return b64encode(path, altchars='+-').replace('=', '*')

    def dec_file(self, b64):
        return b64decode(b64.replace('*', '='), altchars='+-')

    def add_tab(self):
        self._tabs.append(self._root)

    def mode_string(self, mode):
        return ('r' if mode & 256 else '-') + \
           ('w' if mode & 128 else '-') + \
           ('x' if mode & 64 else '-') + \
           ('r' if mode & 32 else '-') + \
           ('w' if mode & 16 else '-') + \
           ('x' if mode & 8 else '-') + \
           ('r' if mode & 4 else '-') + \
           ('w' if mode & 2 else '-') + \
           ('x' if mode & 1 else '-')

    @event('button/click')
    @event('linklabel/click')
    @event('minibutton/click')
    def on_btn_click(self, event, params, vars=None):
        if params[0] == 'btnNewTab':
            self.add_tab()
        if params[0] == 'breadcrumb':
            self._tabs[int(params[1])] = self.dec_file(params[2])
        if params[0] == 'goto':
            self._tab = int(params[1])
            self._tabs[self._tab] = self.dec_file(params[2])
        if params[0] == 'gototab':
            self._tab = len(self._tabs)
            self._tabs.append(self.dec_file(params[2]))
        if params[0] == 'rmClipboard':
            self._clipboard.remove(self._clipboard[int(params[1])])
        if params[0] == 'close' and len(self._tabs)>1:
            self._tabs.remove(self._tabs[int(params[1])])
            self._tab = 0
        if params[0] == 'paste':
            self._tab = int(params[1])
            path = self._tabs[int(params[1])]
            self.work(self._cbs, self._clipboard, path)
        if params[0] == 'newfld':
            self._tab = int(params[1])
            path = self._tabs[int(params[1])]
            try:
                p = os.path.join(path, 'new folder')
                os.mkdir(p)
            except:
                pass
            self._renaming = p
        if params[0] == 'delete':
            self._tab = int(params[1])
            f = self.dec_file(params[2])
            try:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                else:
                    os.unlink(f)
                self.put_message('info', 'Deleted %s'%f)
            except Exception, e:
                self.put_message('err', str(e))
        if params[0] == 'acls':
            self._tab = int(params[1])
            self._editing_acl = self.dec_file(params[2])
        if params[0] == 'delAcl':
            idx = int(params[1])
            del_acl(self._editing_acl, get_acls(self._editing_acl)[idx][0])
            
    @event('form/submit')
    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'files':
            act = vars.getvalue('action', '')
            tab = self._tab
            lst = []
            for x in vars:
                if '/' in x and vars.getvalue(x, None) == '1':
                    tab, f = x.split('/')
                    f = self.dec_file(f)
                    lst.append(f)
            if len(lst) > 0:
                if act == 'copy':
                    self._clipboard = lst
                    self._cbs = 'copy'
                if act == 'cut':
                    self._clipboard = lst
                    self._cbs = 'cut'
                if act == 'rename':
                    self._renaming = lst[0]
            self._tab = tab
        if params[0] == 'dlgRename':
            if vars.getvalue('action', None) == 'OK':
                os.rename(self._renaming,
                    os.path.join(
                        os.path.split(self._renaming)[0],
                        vars.getvalue('value', None)
                    ))
            self._renaming = None
        if params[0] == 'dlgAcl':
            self._editing_acl = None
        if params[0] == 'frmAddAcl':
            if vars.getvalue('action', None) == 'OK':
                set_acl(self._editing_acl, 
                    vars.getvalue('subject', None),
                    vars.getvalue('perm', None),
                    )
        if params[0] == 'edAclPerm':
            idx = int(params[1])
            set_acl(self._editing_acl, get_acls(self._editing_acl)[idx][0], vars.getvalue('value', None))
        if params[0] == 'edAclSubject':
            idx = int(params[1])
            perm = get_acls(self._editing_acl)[idx][1]
            del_acl(self._editing_acl, get_acls(self._editing_acl)[idx][0])
            set_acl(self._editing_acl, vars.getvalue('value', None), perm)

    def work(self, action, files, target):
        w = FMWorker(self, action, files, target)
        self.app.session['fm_worker'] = w
        w.start()

        
class FMWorker(BackgroundWorker):

    def __init__(self, *args):
        self.action = ''
        BackgroundWorker.__init__(self, *args)
    
    def run(self, cat, action, files, target):
        self.action = action
        try:
            for f in files:
                np = os.path.join(target, os.path.split(f)[1])
                if action == 'copy':
                    if (not os.path.isdir(f)) or os.path.islink(f):
                        shutil.copy2(f, np)
                    else:
                        shutil.copytree(f, np, symlinks=True)
                if action == 'cut':
                    os.rename(f, np)
        except Exception, e:
            cat.put_message('err', str(e))

    def get_status(self):
        return self.action


class FMProgress(Plugin):
    implements(IProgressBoxProvider)
    title = 'File manager'
    icon = '/dl/fm/icon.png'
    can_abort = True

    def get_worker(self):
        try:
            return self.app.session['fm_worker']
        except:
            return None

    def has_progress(self):
        if self.get_worker() is None:
            return False
        return self.get_worker().alive

    def get_progress(self):
        return self.get_worker().get_status()

    def abort(self):
        if self.has_progress():
            self.get_worker().kill()
