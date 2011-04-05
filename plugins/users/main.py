from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import *

from backend import *


class UsersPlugin(CategoryPlugin):
    text = 'Users'
    icon = '/dl/users/icon.png'
    folder = 'system'

    params = {
            'login': 'Login',
            'password': 'Password',
            'name': 'Name',
            'uid': 'UID',
            'gid': 'GID',
            'ggid': 'GID',
            'home': 'Home directory',
            'shell': 'Shell',
            'groups': 'Groups',
            'adduser': 'New user login',
            'addgrp': 'New group name',
            'addtogroup': 'Add to group',
            'delfromgroup': 'Delete from group',
        }

    gparams = {
            'gname': 'Name',
            'ggid': 'GID',
        }

    def on_init(self):
        self.backend = UsersBackend(self.app)
        
    def get_config(self):
        return self.app.get_config(self.backend)
        
    def on_session_start(self):
        self._tab = 0
        self._selected_user = ''
        self._selected_group = ''
        self._editing = ''

    def get_ui(self):
        self.users = self.backend.get_all_users()
        self.groups = self.backend.get_all_groups()
        self.backend.map_groups(self.users, self.groups)

        ui = self.app.inflate('users:main')
        ui.find('tabs').set('active', self._tab)

        if self._editing != '':
            if self._editing in self.params:
                ui.find('dlgEdit').set('text', self.params[self._editing])
            else:
                ui.find('dlgEdit').set('text', self.gparams[self._editing])
        else:
            ui.remove('dlgEdit')

        # Users
        t = ui.find('userlist') 
        
        for u in self.users:
            t.append(UI.DataTableRow(
                    UI.DataTableCell(
                        UI.Image(file='/dl/core/ui/stock/user.png'),
                        UI.Label(text=u.login, bold=True)
                    ),
                    UI.Label(text=u.uid, bold=(u.uid>=1000)),
                    UI.Label(text=u.home),
                    UI.Label(text=u.shell),
                    UI.DataTableCell(
                        UI.MiniButton(id='edit/'+u.login, text='Edit'),
                        hidden=True
                    )
                ))

        if self._selected_user != '':
            u = self.backend.get_user(self._selected_user, self.users)
            self.backend.map_groups([u], self.backend.get_all_groups())

            ui.find('lblulogin').set('text', 'Login: '+ u.login)
            ui.find('deluser').set('msg', 'Delete user %s'%u.login)
            ui.find('lbluuid').set('text', 'UID: '+ str(u.uid))
            ui.find('lblugid').set('text', 'GID: '+ str(u.gid))
            ui.find('lbluhome').set('text', 'Home: '+ u.home)
            ui.find('lblushell').set('text', 'Shell: '+ u.shell)
            ui.find('lblugroups').set('text', ', '.join(u.groups))
        else:
            ui.remove('dlgEditUser')
            
            
        # Groups
        t = ui.find('grouplist')

        for u in self.groups:
            t.append(UI.DataTableRow(
                    UI.DataTableCell(
                        UI.Image(file='/dl/core/ui/stock/group.png'),
                        UI.Label(text=u.name, bold=True)
                    ),
                    UI.Label(text=u.gid, bold=(u.gid>=1000)),
                    UI.Label(text=', '.join(u.users)),
                    UI.DataTableCell(
                        UI.MiniButton(id='gedit/'+u.name, text='Select'),
                        hidden=True
                    )
                ))

        if self._selected_group != '':
            t = UI.Container(t, self.get_ui_edit_group())
    
            u = self.backend.get_group(self._selected_group, self.groups)
            g = ', '.join(u.users)

            ui.find('lblgname').set('text', 'Name: '+ u.name)
            ui.find('delgroup').set('msg', 'Delete group %s'%u.name)
            ui.find('lblggid').set('text', 'GID: '+ str(u.gid))
            ui.find('lblgusers').set('text', g)
        else:
            ui.remove('dlgEditGroup')

        return ui

    @event('minibutton/click')
    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'edit':
            self._tab = 0
            self._selected_user = params[1]
        if params[0] == 'gedit':
            self._tab = 1
            self._selected_group = params[1]
        if params[0].startswith('ch'):
            self._tab = 0
            self._editing = params[0][2:]
        if params[0] == 'adduser':
            self._tab = 0
            self._editing = 'adduser'
        if params[0] == 'addgrp':
            self._tab = 1
            self._editing = 'addgrp'
        if params[0] == 'deluser':
            self._tab = 0
            self.backend.del_user(self._selected_user)
            self._selected_user = ''
        if params[0] == 'delgroup':
            self._tab = 1
            self.backend.del_group(self._selected_group)
            self._selected_group = ''

    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEdit':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                if self._editing == 'adduser':
                    self.backend.add_user(v)
                    self._selected_user = v
                elif self._editing == 'addgrp':
                    self.backend.add_group(v)
                    self._selected_group = v
                elif self._editing == 'addtogroup':
                    self.backend.add_to_group(self._selected_user, v)
                elif self._editing == 'delfromgroup':
                    self.backend.remove_from_group(self._selected_user, v)
                elif self._editing == 'password':
                    self.backend.change_user_password(self._selected_user, v)
                elif self._editing == 'login':
                    self.backend.change_user_param(self._selected_user, self._editing, v)
                    self._selected_user = v
                elif self._editing in self.params:
                    self.backend.change_user_param(self._selected_user, self._editing, v)
                elif self._editing in self.gparams:
                    self.backend.change_group_param(self._selected_group, self._editing, v)
            self._editing = ''
        if params[0] == 'dlgEditUser':
            self._selected_user = ''
        if params[0] == 'dlgEditGroup':
            self._selected_group = ''

