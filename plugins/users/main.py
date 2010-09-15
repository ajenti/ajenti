from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import *

import backend


class UsersPlugin(CategoryPlugin):
    text = 'Users'
    icon = '/dl/users/icon_small.png'
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
            'adduser': 'New user login',
            'addgrp': 'New group name'
        }

    def on_session_start(self):
        self._tab = 0
        self._selected_user = ''
        self._selected_group = ''
        self._editing = ''

    def get_ui(self):
        panel = UI.PluginPanel(UI.Label(), title='User accounts', icon='/dl/users/icon.png')

        panel.appendChild(self.get_default_ui())

        return panel

    def get_default_ui(self):
        self.users = backend.get_all_users()
        self.groups = backend.get_all_groups()
        backend.map_groups(self.users, self.groups)

        tc = UI.TabControl(active=self._tab)
        tc.add('Users', self.get_ui_users())
        tc.add('Groups', self.get_ui_groups())

        if self._editing != '':
            tc = UI.VContainer(tc, UI.InputBox(title=self.params[self._editing], id='dlgEdit'))
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
            t.appendChild(UI.DataTableRow(
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
            t.appendChild(UI.DataTableRow(
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
        u = backend.get_user(self._selected_user, self.users)
        backend.map_groups([u], backend.get_all_groups())
        g = ', '.join(u.groups)

        dlg = UI.DialogBox(
                UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Label(text='Login: '+ u.login, bold=True),
                        UI.Button(text='Change', id='chlogin')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(),
                        UI.Button(text='Change password', id='chpasswd')
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
                        UI.Button(text='Edit', id='chgroups')
                    ),
                    UI.LayoutTableRow(
                        UI.LayoutTableCell(
                            UI.Label(text=g),
                            colspan=2
                        )
                    )
                ),
                title='Edit user',
                id='dlgEditUser'
              )
        return dlg

    def get_ui_edit_group(self):
        u = backend.get_group(self._selected_group, self.groups)
        g = ', '.join(u.users)

        dlg = UI.DialogBox(
                UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Label(text='Name: ' + u.name, bold=True),
                        UI.Button(text='Change', id='gchname')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(),
                        UI.WarningButton(text='Delete group', id='delgroup', msg='Delete group %s'%u.name)
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='GID: ' + str(u.gid)),
                        UI.Button(text='Change', id='gchgid')
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
        if params[0] == 'chlogin':
            self._tab = 0
            self._editing = 'login'
        if params[0] == 'chuid':
            self._tab = 0
            self._editing = 'uid'
        if params[0] == 'chgid':
            self._tab = 0
            self._editing = 'gid'
        if params[0] == 'chshell':
            self._tab = 0
            self._editing = 'shell'
        if params[0] == 'chpasswd':
            self._tab = 0
            self._editing = 'password'
        if params[0] == 'chhome':
            self._tab = 0
            self._editing = 'home'
        if params[0] == 'gchname':
            self._tab = 1
            self._editing = 'name'
        if params[0] == 'gchgid':
            self._tab = 1
            self._editing = 'ggid'
        if params[0] == 'adduser':
            self._tab = 0
            self._editing = 'adduser'
        if params[0] == 'addgrp':
            self._tab = 1
            self._editing = 'addgrp'
        if params[0] == 'deluser':
            self._tab = 0
            backend.del_user(self._selected_user)
            self._selected_user = ''
        if params[0] == 'delgroup':
            self._tab = 1
            backend.del_group(self._selected_group)
            self._selected_group = ''

    @event('dialog/submit')
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


class UsersContent(ModuleContent):
    module = 'users'
    path = __file__
