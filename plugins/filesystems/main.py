from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import *

import backend

class FSPlugin(CategoryPlugin):
    implements((ICategoryProvider, 60))

    text = 'Filesystems'
    icon = '/dl/filesystems/icon.png'
        
    def on_init(self):
        self.fstab = backend.read()
        
    def on_session_start(self):
        self._log = ''
        self._tree = TreeManager()
        
    def get_ui(self):
        panel = UI.PluginPanel(UI.Label(text=self._log), title='Mounted filesystems', icon='/dl/filesystems/icon.png')

        panel.appendChild(self.get_default_ui())        

        return panel

    def get_default_ui(self):
        t = UI.DataTable(UI.DataTableRow(
                UI.Label(text='Source'),
                UI.Label(text='Mountpoint'),
                UI.Label(text='FS type'),
                UI.Label(text='Options'),
                UI.Label(),
                UI.Label(),
                UI.Label(), header=True
               ))
        for u in self.fstab:       
            t.appendChild(UI.DataTableRow(
                    UI.Label(text=u.src, bold=True),
                    UI.Label(text=u.dst),
                    UI.Label(text=u.fs_type),
                    UI.Label(text=u.options),
                    UI.Label(text=str(u.dump_p)),
                    UI.Label(text=str(u.fsck_p)),
                    UI.DataTableCell(
                        UI.HContainer(
                            UI.MiniButton(id='edit/'+str(self.fstab.index(u)), text='Edit'),
                            UI.MiniButton(id='del/'+str(self.fstab.index(u)), text='Delete')
                        ),
                        hidden=True
                    )
                ))
        return t
        
    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        pass
        
"""   @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEdit':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                if self._editing == 'adduser':
                    backend.add_user(v)
                    self._selected_user = v
                if self._editing == 'addgrp':
                    backend.add_group(v)
                    self._selected_group = v
                if self._editing == 'login':
                    backend.change_user_login(self._selected_user, v)
                    self._selected_user = v
                if self._editing == 'uid':
                    backend.change_user_uid(self._selected_user, v)
                if self._editing == 'gid':
                    backend.change_user_gid(self._selected_user, v)
                if self._editing == 'shell':
                    backend.change_user_shell(self._selected_user, v)
                if self._editing == 'password':
                    backend.change_user_password(self._selected_user, v)
                if self._editing == 'home':
                    backend.change_user_home(self._selected_user, v)
                if self._editing == 'name':
                    backend.change_group_name(self._selected_group, v)
                    self._selected_group = v
                if self._editing == 'ggid':
                    backend.change_group_gid(self._selected_group, v)
            self._editing = '' 
        if params[0] == 'dlgEditUser':
            self._selected_user = '' 
        if params[0] == 'dlgEditGroup':
            self._selected_group = '' 
"""
        
class FSContent(ModuleContent):
    module = 'filesystems'
    path = __file__
    
    
