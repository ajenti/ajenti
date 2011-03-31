# coding: utf-8
from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import shell, enquote, BackgroundProcess
from ajenti.plugins.core.api import *
from ajenti.utils import *
import os
from base64 import b64encode, b64decode
from stat import ST_UID, ST_GID, ST_MODE, ST_SIZE
import grp, pwd

class FMPlugin(CategoryPlugin):
    text = 'File manager'
    icon = '/dl/fm/icon.png'
    folder = 'tools'

    def on_session_start(self):
        self._root = self.app.get_config(self).dir
        self._tabs = []
        self._tab = 0
        self.add_tab()
        
    def get_ui(self):
        ui = self.app.inflate('fm:main')
        tc = UI.TabControl(active=self._tab)

        for tab in self._tabs:
            tc.add(tab, self.get_tab(tab))

        ui.append('main', tc)
        return ui

    def get_tab(self, tab):
        ui = self.app.inflate('fm:tab')

        tidx = self._tabs.index(tab)
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

            user = pwd.getpwuid(stat[ST_UID])[0]
            group = grp.getgrgid(stat[ST_GID])[0]

            name = f
            if islink:
                name += ' → ' + os.path.realpath(np)
                
            row = UI.DataTableRow(
                UI.Checkbox(id='file/%i/%s' % (
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
                ),
                UI.Label(text=size),
                UI.Label(text='%s:%s'%(user,group), monospace=True),
                UI.Label(text=self.mode_string(mode), monospace=True),
            )

            ui.append('list', row)
        return ui

    def enc_file(self, path):
        path = path.replace('//','/')
        return b64encode(path, altchars='+-')

    def dec_file(self, b64):
        return b64decode(b64, altchars='+-')

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
    def on_btn_click(self, event, params, vars=None):
        if params[0] == 'btnNewTab':
            self.add_tab()
        if params[0] == 'breadcrumb':
            self._tabs[int(params[1])] = self.dec_file(params[2])
        if params[0] == 'goto':
            self._tab = int(params[1])
            self._tabs[self._tab] = self.dec_file(params[2])

    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        text = vars.getvalue('text', None)
        if text is not None:
            open(self._file, 'w').write(text)
            self.put_message('info', 'Saved')
            if vars.getvalue('action', '') == 'fav':
                self._favs.append(self._file)
            if vars.getvalue('action', '') == 'unfav':
                self._favs.remove(self._file)
            self.app.config.set('notepad', 'favs', '|'.join(self._favs))
            self.app.config.save()
            
            
