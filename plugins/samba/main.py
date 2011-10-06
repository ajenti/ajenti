from ajenti.api import *
from ajenti.ui import *
from ajenti.utils import *
from ajenti import apis

import backend


class SambaPlugin(apis.services.ServiceControlPlugin):
    text = 'Samba'
    icon = '/dl/samba/icon.png'
    folder = 'servers'
    service_name = 'smbd'
    
    def on_session_start(self):
        self._tab = 0
        self._cfg = backend.SambaConfig(self.app)
        if backend.is_installed():
            self._cfg.load()
        self._editing_share = None
        self._editing_user = None
        self._editing = None
        self._adding_user = False

    def get_main_ui(self):
        ui = self.app.inflate('samba:main')
        ui.find('tabs').set('active', self._tab)

        # Shares
        for h in self._cfg.get_shares():
            r = UI.DTR(
                    UI.Image(file='/dl/core/ui/stock/folder.png'),
                    UI.Label(text=h),
                    UI.Label(text=self._cfg.shares[h]['path']),
                    UI.HContainer(
                        UI.TipIcon(icon='/dl/core/ui/stock/edit.png',
                            text='Edit', id='editshare/' + h),
                        UI.TipIcon(
                            icon='/dl/core/ui/stock/delete.png',
                            text='Delete', id='delshare/' + h, warning='Delete share %s'%h)
                    ),
                )
            ui.append('shares', r)

        if not self._editing_share is None:
            if self._editing_share == '':
                ui.append('main', self.get_ui_edit_share())
            else:
                ui.append('main', self.get_ui_edit_share(
                            self._cfg.shares[self._editing_share]
                        ))


        # Users
        for h in sorted(self._cfg.users.keys()):
            r = UI.DTR(
                    UI.Image(file='/dl/core/ui/stock/user.png'),
                    UI.Label(text=h),
                    UI.HContainer(
                        UI.TipIcon(icon='/dl/core/ui/stock/edit.png',
                            text='Edit', id='edituser/' + h),
                        UI.TipIcon(
                            icon='/dl/core/ui/stock/delete.png',
                            text='Delete', id='deluser/' + h, warning='Delete user %s'%h)
                    ),
                )
            ui.append('users', r)


        if not self._editing_user is None:
            if self._editing_user == '':
                ui.append('main', self.get_ui_edit_user())
            else:
                ui.append('main', self.get_ui_edit_user(
                            self._cfg.users[self._editing_user]
                        ))

        if not self._editing is None:
            ui.append('main', UI.InputBox(
                title=self._editing,
                value=self._cfg.users[self._editing_user][self._editing],
                id='dlgEdit'
            ))

        if self._adding_user:
            ui.append('main', UI.InputBox(
                title='New user',
                text='Unix login:',
                id='dlgAddUser'
            ))

    
        # Config
        ui.append('tab2', self.get_ui_general())
        
        return ui


    def get_ui_edit_share(self, s=None):
        if s is None or s == '':
            s = self._cfg.new_share()

        dlg = UI.DialogBox(
                  UI.Container(
                      UI.Formline(
                          UI.TextInput(name='name', value='new'),
                          text='Name',
                      ) if self._editing_share == '' else None,
                      UI.Formline(
                          UI.TextInput(name='path', value=s['path']),
                          text='Path',
                      ),
                      UI.Formline(
                          UI.TextInput(name='valid users', value=s['valid users']),
                          text='Valid users',
                      ),
                      UI.Formline(
                          UI.Checkbox( name='available', checked=s['available']=='yes'),
                          text='Available',
                      ),
                      UI.Formline(
                          UI.Checkbox(name='browseable', checked=s['browseable']=='yes'),
                          text='Browseable', 
                      ),
                      UI.Formline(
                          UI.Checkbox(name='read only', checked=s['read only']=='yes'),
                          text='Read only',
                      ),
                      UI.Formline(
                          UI.Checkbox(name='guest ok', checked=s['guest ok']=='yes'),
                          text='Guest access'
                      ),
                      UI.Formline(
                          UI.Checkbox(name='guest only', checked=s['guest only']=='yes'),
                          text='Force guest',
                      )
                  ),
                  id='dlgEditShare',
                  title='Edit share'
              )
        return dlg

    def get_ui_edit_user(self, u=None):
        t = UI.Container()
        for k in self._cfg.fields:
            if k in u.keys():
              t.append(
                    UI.Formline(
                        UI.Label(text=u[k]),
                        UI.Button(design='mini',
                          text='Change', id='chuser/'+k) if k in self._cfg.editable else None,
                        text=k
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
                  UI.Formline(
                      UI.TextInput(name='server string', value=self._cfg.general['server string']),
                      text='Machine description',
                  ),
                  UI.Formline(
                      UI.TextInput(name='workgroup', value=self._cfg.general['workgroup']),
                      text='Workgroup',
                  ),
                  UI.Formline(
                      UI.TextInput(name='interfaces', value=self._cfg.general['interfaces']),
                      text='Listen on interfaces',
                  ),
                  UI.Formline(
                      UI.TextInput(name='socket options', value=self._cfg.general['socket options']),
                      text='Socket options',
                  ),
                  UI.Formline(
                      UI.SelectInput(
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
                      ),
                      text='Security',
                  ),
                  UI.Formline(
                      UI.TextInput(name='password server', value=self._cfg.general['password server']),
                      text='Password server',
                  ),
                  id='frmGeneral'
              )
        return dlg

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