from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import *
from ajenti import apis

import backend


class SambaPlugin(apis.services.ServiceControlPlugin):
    text = 'Samba'
    icon = '/dl/samba/icon_small.png'
    folder = 'servers'
    service_name = 'smbd'
    
    def on_session_start(self):
        self._tab = 0
        self._cfg = backend.SambaConfig()
        if backend.is_installed():
            self._cfg.load()
        self._editing_share = None
        self._editing_user = None
        self._editing = None
        self._adding_user = False

    def get_main_ui(self):
        panel = UI.ServicePluginPanel(title='Samba', icon='/dl/samba/icon.png', status=self.service_status, servicename=self.service_name)

        if not backend.is_installed():
            panel.append(UI.VContainer(UI.ErrorBox(title='Error', text='Samba is not installed')))
        else:
            panel.append(self.get_default_ui())

        return panel

    def get_default_ui(self):
        tc = UI.TabControl(active=self._tab)
        tc.add('Shares', self.get_ui_shares())
        tc.add('Users', self.get_ui_users())
        tc.add('General', self.get_ui_general())
        return tc

    def get_ui_shares(self):
        th = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Name'), width='200px'),
                UI.DataTableCell(UI.Label(text='Path'), width='200px'),
                UI.DataTableCell(UI.Label()),
                header=True
             )
        th.append(hr)

        for h in self._cfg.get_shares():
            r = UI.DataTableRow(
                    UI.DataTableCell(
                        UI.Image(file='/dl/core/ui/stock/folder.png'),
                        UI.Label(text=h)
                    ),
                    UI.Label(text=self._cfg.shares[h]['path']),
                    UI.DataTableCell(
                        UI.HContainer(
                            UI.MiniButton(text='Edit', id='editshare/' + h),
                            UI.WarningMiniButton(text='Delete', id='delshare/' + h, msg='Delete share %s'%h)
                        ),
                        hidden=True
                    )
                )
            th.append(r)

        th = UI.VContainer(th, UI.Button(text='Add new share', id='newshare'))

        if not self._editing_share is None:
            if self._editing_share == '':
                th.append(self.get_ui_edit_share())
            else:
                th.append(self.get_ui_edit_share(
                            self._cfg.shares[self._editing_share]
                        ))
        return th

    def get_ui_users(self):
        th = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Name'), width='200px'),
                UI.DataTableCell(UI.Label()),
                header=True
             )
        th.append(hr)

        for h in sorted(self._cfg.users.keys()):
            r = UI.DataTableRow(
                    UI.DataTableCell(
                        UI.Image(file='/dl/core/ui/stock/user.png'),
                        UI.Label(text=h)
                    ),
                    UI.DataTableCell(
                        UI.HContainer(
                            UI.MiniButton(text='Edit', id='edituser/' + h),
                            UI.WarningMiniButton(text='Delete', id='deluser/' + h, msg='Delete user %s'%h)
                        ),
                        hidden=True
                    )
                )
            th.append(r)

        th = UI.VContainer(th, UI.Button(text='Add new user', id='newuser'))

        if not self._editing_user is None:
            if self._editing_user == '':
                th.append(self.get_ui_edit_user())
            else:
                th.append(self.get_ui_edit_user(
                            self._cfg.users[self._editing_user]
                        ))

        if not self._editing is None:
            th.append(UI.InputBox(
                title=self._editing,
                value=self._cfg.users[self._editing_user][self._editing],
                id='dlgEdit'
            ))

        if self._adding_user:
            th.append(UI.InputBox(
                title='New user',
                text='Unix login:',
                id='dlgAddUser'
            ))

        return th


    def get_ui_edit_share(self, s=None):
        if s is None or s == '':
            s = self._cfg.new_share()

        dlg = UI.DialogBox(
                  UI.LayoutTable(
                      UI.LayoutTableRow(
                          UI.Label(text='Name:'),
                          UI.TextInput(name='name', value='new')
                      ) if self._editing_share == '' else None,
                      UI.LayoutTableRow(
                          UI.Label(text='Path:'),
                          UI.TextInput(name='path', value=s['path'])
                      ),
                      UI.LayoutTableRow(
                          UI.Label(text='Valid users:'),
                          UI.TextInput(name='valid users', value=s['valid users'])
                      ),
                      UI.LayoutTableRow(
                          UI.LayoutTableCell(
                              UI.Checkbox(text='Available', name='available', checked=s['available']=='yes'),
                              colspan=2
                          )
                      ),
                      UI.LayoutTableRow(
                          UI.LayoutTableCell(
                              UI.Checkbox(text='Browseable', name='browseable', checked=s['browseable']=='yes'),
                              colspan=2
                          )
                      ),
                      UI.LayoutTableRow(
                          UI.LayoutTableCell(
                              UI.Checkbox(text='Read only', name='read only', checked=s['read only']=='yes'),
                              colspan=2
                          )
                      ),
                      UI.LayoutTableRow(
                          UI.LayoutTableCell(
                              UI.Checkbox(text='Guest access', name='guest ok', checked=s['guest ok']=='yes'),
                              colspan=2
                          )
                      ),
                      UI.LayoutTableRow(
                          UI.LayoutTableCell(
                              UI.Checkbox(text='Force guest', name='guest only', checked=s['guest only']=='yes'),
                              colspan=2
                          )
                      )
                  ),
                  id='dlgEditShare',
                  title='Edit share'
              )
        return dlg

    def get_ui_edit_user(self, u=None):
        t = UI.LayoutTable()
        for k in self._cfg.fields:
            t.append(
                UI.LayoutTableRow(
                    UI.Label(text=k+':'),
                    UI.Label(text=u[k]),
                    UI.Button(text='Change', id='chuser/'+k) if k in self._cfg.editable else None
                )
            )

        dlg = UI.DialogBox(
                t,
                title='Edit user',
                id='dlgEditUser'
              )
        return dlg


    def get_ui_general(self):
        dlg = UI.FormBox(
                  UI.LayoutTable(
                      UI.LayoutTableRow(
                          UI.Label(text='Machine description:'),
                          UI.TextInput(name='server string', value=self._cfg.general['server string'])
                      ),
                      UI.LayoutTableRow(
                          UI.Label(text='Workgroup:'),
                          UI.TextInput(name='workgroup', value=self._cfg.general['workgroup'])
                      ),
                      UI.LayoutTableRow(
                          UI.Label(text='Listen on interfaces:'),
                          UI.TextInput(name='interfaces', value=self._cfg.general['interfaces'])
                      ),
                      UI.LayoutTableRow(
                          UI.Label(text='Socket options:'),
                          UI.TextInput(name='socket options', value=self._cfg.general['socket options'])
                      ),
                      UI.LayoutTableRow(
                          UI.Label(text='Security:'),
                          UI.Select(
                              UI.SelectOption(text='Share', value='share',
                                    selected=self._cfg.general['security']=='share'),
                              UI.SelectOption(text='User', value='user',
                                    selected=self._cfg.general['security']=='user'),
                              UI.SelectOption(text='Password', value='password',
                                    selected=self._cfg.general['security']=='password'),
                              UI.SelectOption(text='Other server', value='server',
                                    selected=self._cfg.general['security']=='server'),
                              UI.SelectOption(text='Active Directory', value='ads',
                                    selected=self._cfg.general['security']=='ads'),
                              name='security'
                          )
                      ),
                      UI.LayoutTableRow(
                          UI.Label(text='Password server:'),
                          UI.TextInput(name='password server', value=self._cfg.general['password server'])
                      )
                  ),
                  id='frmGeneral'
              )
        return dlg

    @event('minibutton/click')
    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'restart':
            backend.restart()
        if params[0] == 'editshare':
            self._editing_share = params[1]
            self._tab = 0
        if params[0] == 'delshare':
            self._cfg.shares.pop(params[1])
            self._cfg.save()
            self._tab = 0
        if params[0] == 'newshare':
            self._editing_share = ''
            self._tab = 0
        if params[0] == 'edituser':
            self._editing_user = params[1]
            self._tab = 1
        if params[0] == 'newuser':
            self._adding_user = True
            self._tab = 1
        if params[0] == 'deluser':
            self._cfg.del_user(params[1])
            self._cfg.load()
            self._tab = 1
        if params[0] == 'chuser':
            self._tab = 1
            self._editing = params[1]

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEditShare':
            if vars.getvalue('action', '') == 'OK':
                es = self._editing_share
                if es == '':
                    es = vars.getvalue('name', 'new')
                    self._cfg.shares[es] = self._cfg.new_share()

                self._cfg.set_param_from_vars(es, 'path', vars)
                self._cfg.set_param_from_vars(es, 'valid users', vars)
                self._cfg.set_param_from_vars_yn(es, 'available', vars)
                self._cfg.set_param_from_vars_yn(es, 'browseable', vars)
                self._cfg.set_param_from_vars_yn(es, 'read only', vars)
                self._cfg.set_param_from_vars_yn(es, 'guest ok', vars)
                self._cfg.set_param_from_vars_yn(es, 'guest only', vars)
                self._cfg.save()
            self._editing_share = None

        if params[0] == 'frmGeneral':
            if vars.getvalue('action', '') == 'OK':
                self._cfg.set_param_from_vars('general', 'server string', vars)
                self._cfg.set_param_from_vars('general', 'workgroup', vars)
                self._cfg.set_param_from_vars('general', 'interfaces', vars)
                self._cfg.set_param_from_vars('general', 'socket options', vars)
                self._cfg.set_param_from_vars('general', 'security', vars)
                self._cfg.set_param_from_vars('general', 'password server', vars)
                self._cfg.save()
            self._tab = 2

        if params[0] == 'dlgEditUser':
            self._editing_user = None

        if params[0] == 'dlgAddUser':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                if v != '':
                    self._cfg.add_user(v)
                    self._cfg.load()
                    self._editing_user = v
            self._adding_user = False

        if params[0] == 'dlgEdit':
            if vars.getvalue('action', '') == 'OK':
                self._cfg.modify_user(self._editing_user, self._editing, vars.getvalue('value', ''))
                self._cfg.load()
            self._editing = None


class SambaContent(ModuleContent):
    module = 'samba'
    path = __file__
