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
        panel = UI.PluginPanel(UI.Label(), title='User accounts', icon='/dl/users/icon.png')
        panel.append(self.get_default_ui())
        return panel

    def get_default_ui(self):
        self.users = self.backend.get_all_users()
        self.groups = self.backend.get_all_groups()
        self.backend.map_groups(self.users, self.groups)

        tc = UI.TabControl(active=self._tab)
        tc.add('Users', self.get_ui_users())
        tc.add('Groups', self.get_ui_groups())

        if self._editing != '':
            if self._editing in self.params:
                tc = UI.VContainer(tc, UI.InputBox(text=self.params[self._editing], id='dlgEdit'))
            else:
                tc = UI.VContainer(tc, UI.InputBox(text=self.gparams[self._editing], id='dlgEdit'))
        return tc

    def get_ui_users(self):
        t = UI.DataTable(UI.DataTableRow(
                UI.Label(text='Login'),
                UI.Label(text='UID'),
                UI.Label(text='Home'),
                UI.Label(text='Shell'),
                UI.Label(), header=True
               ))
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
                        UI.MiniButton(id='edit/'+u.login, text='Select'),
                        hidden=True
                    )
                ))

        t = UI.VContainer(t, UI.Button(text='Add user', id='adduser'))
        if self._selected_user != '':
            t = UI.Container(t, self.get_ui_edit_user())
        return t

    def get_ui_groups(self):
        t = UI.DataTable(UI.DataTableRow(
                UI.Label(text='Name'),
                UI.Label(text='GID'),
                UI.Label(text='Users'),
                UI.Label(), header=True
               ))
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

        t = UI.VContainer(t, UI.Button(text='Add group', id='addgrp'))
        if self._selected_group != '':
            t = UI.Container(t, self.get_ui_edit_group())
        return t

    def get_ui_edit_user(self):
        u = self.backend.get_user(self._selected_user, self.users)
        self.backend.map_groups([u], self.backend.get_all_groups())

        dlg = UI.DialogBox(
                UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Label(text='Login: '+ u.login, bold=True),
                        UI.Button(text='Change', id='chlogin')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(),
                        UI.Button(text='Change password', id='chpassword')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(),
                        UI.WarningButton(text='Delete user', id='deluser', msg='Delete user %s'%u.login)
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='UID: '+ str(u.uid)),
                        UI.Button(text='Change', id='chuid')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='GID: '+ str(u.gid)),
                        UI.Button(text='Change', id='chgid')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Home directory: '+ u.home),
                        UI.Button(text='Change', id='chhome')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Shell: '+ u.shell),
                        UI.Button(text='Change', id='chshell')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Groups: '),
                        UI.LayoutTableCell(
                            UI.MiniButton(text='Add', id='chaddtogroup'),
                            UI.MiniButton(text='Delete', id='chdelfromgroup')
                        )      
                    ),
                    UI.LayoutTableRow(
                        UI.LayoutTableCell(
                            UI.Label(text=', '.join(u.groups)),
                            colspan=2
                        )
                    )
                ),
                title='Edit user',
                hidecancel=True,
                id='dlgEditUser'
              )
        return dlg

    def get_ui_edit_group(self):
        u = self.backend.get_group(self._selected_group, self.groups)
        g = ', '.join(u.users)

        dlg = UI.DialogBox(
                UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Label(text='Name: ' + u.name, bold=True),
                        UI.Button(text='Change', id='chgname')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(),
                        UI.WarningButton(text='Delete group', id='delgroup', msg='Delete group %s'%u.name)
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='GID: ' + str(u.gid)),
                        UI.Button(text='Change', id='chggid')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Users: '),
                        UI.Label()
                    ),
                    UI.LayoutTableRow(
                        UI.LayoutTableCell(
                            UI.Label(text=g),
                            colspan=2
                        )
                    )
                ),
                title='Edit group',
                hidecancel=True,
                id='dlgEditGroup'
              )
        return dlg

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

