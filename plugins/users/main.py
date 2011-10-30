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
        self.users = self.backend.get_all_users()
        self.groups = self.backend.get_all_groups()
        self.backend.map_groups(self.users, self.groups)

    def reload_data(self):
        self.users = self.backend.get_all_users()
        self.groups = self.backend.get_all_groups()
        self.backend.map_groups(self.users, self.groups)

    def get_config(self):
        return self.app.get_config(self.backend)

    def on_session_start(self):
        self._tab = 0
        self._selected_user = ''
        self._selected_group = ''
        self._editing = ''

    def get_ui(self):
        self.reload_data()
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
            t.append(UI.DTR(
                    UI.Image(file='/dl/core/ui/stock/user.png'),
                    UI.Label(text=u.login, bold=True),
                    UI.Label(text=u.uid, bold=(u.uid>=1000)),
                    UI.Label(text=u.home),
                    UI.Label(text=u.shell),
                    UI.TipIcon(icon='/dl/core/ui/stock/edit.png', id='edit/'+u.login, text='Edit'),
                ))

        if self._selected_user != '':
            u = self.backend.get_user(self._selected_user, self.users)
            self.backend.map_groups([u], self.backend.get_all_groups())

            ui.find('elogin').set('value', u.login)
            ui.find('deluser').set('warning', 'Delete user %s'%u.login)
            ui.find('euid').set('value', str(u.uid))
            ui.find('egid').set('value', str(u.gid))
            ui.find('ehome').set('value', u.home)
            ui.find('eshell').set('value', u.shell)
            ui.find('lblugroups').set('text', ', '.join(u.groups))
        else:
            ui.remove('dlgEditUser')


        # Groups
        t = ui.find('grouplist')

        for u in self.groups:
            t.append(UI.DTR(
                    UI.Image(file='/dl/core/ui/stock/group.png'),
                    UI.Label(text=u.name, bold=True),
                    UI.Label(text=u.gid, bold=(u.gid>=1000)),
                    UI.Label(text=', '.join(u.users)),
                    UI.TipIcon(icon='/dl/core/ui/stock/edit.png', id='gedit/'+u.name, text='Edit'),
                ))

        if self._selected_group != '':
            u = self.backend.get_group(self._selected_group, self.groups)
            g = ', '.join(u.users)

            ui.find('ename').set('value', u.name)
            ui.find('delgroup').set('warning', 'Delete group %s'%u.name)
            ui.find('eggid').set('value', str(u.gid))
            ui.find('lblgusers').set('text', g)
        else:
            ui.remove('dlgEditGroup')

        return ui

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
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEdit':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                if self._editing == 'adduser':
                    self.reload_data()
                    for u in self.users:
                        if u.login == v:
                            self.put_message('err', 'Duplicate name')
                            self._editing = ''
                            return
                    self.backend.add_user(v)
                    self._selected_user = v
                elif self._editing == 'addgrp':
                    self.reload_data()
                    for u in self.groups:
                        if u.name == v:
                            self.put_message('err', 'Duplicate name')
                            self._editing = ''
                            return
                    self.backend.add_group(v)
                    self._selected_group = v
                elif self._editing == 'addtogroup':
                    self.backend.add_to_group(self._selected_user, v)
                elif self._editing == 'delfromgroup':
                    self.backend.remove_from_group(self._selected_user, v)
            self._editing = ''
        if params[0].startswith('e'):
            editing = params[0][1:]
            v = vars.getvalue('value', '')
            if editing == 'password':
                self.backend.change_user_password(self._selected_user, v)
            elif editing == 'login':
                self.backend.change_user_param(self._selected_user, editing, v)
                self._selected_user = v
            elif editing in self.params:
                self.backend.change_user_param(self._selected_user, editing, v)
            elif editing in self.gparams:
                self.backend.change_group_param(self._selected_group, editing, v)
            self._editing = None
        if params[0] == 'dlgEditUser':
            self._selected_user = ''
        if params[0] == 'dlgEditGroup':
            self._selected_group = ''
