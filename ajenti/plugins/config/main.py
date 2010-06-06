import platform

from hashlib import sha1
from base64 import b64encode

from ajenti import version
from ajenti.com import *
from ajenti.ui import *
from ajenti.utils import detect_distro
from ajenti.app.helpers import *

class ConfigContent(ModuleContent):
    path = __file__
    module = 'config' 

class Config(CategoryPlugin):
    text = 'Configure'
    icon = '/dl/config/icon.png'

    implements((ICategoryProvider, 9000))

    def on_session_start(self):
        self._tab = 0
        self._adding_user = False

    def get_ui(self):
        u = UI.PluginPanel(UI.Label(text='Ajenti %s' % version), title='Ajenti configuration', icon='/dl/config/icon.png')
        
        tabs = UI.TabControl(active=self._tab)
        tabs.add('General', self.get_ui_general())
        tabs.add('Security', self.get_ui_sec())
        
        u.appendChild(tabs)
        return u
        
    def get_ui_general(self):
        o = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.Label(text='Bind to host:'),
                    UI.TextInput(name='bind_host', value=self.config.get('ajenti', 'bind_host'))
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Bind to port:'),
                    UI.TextInput(name='bind_port', value=self.config.get('ajenti', 'bind_port'))
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Enable SSL:'),
                    UI.Checkbox(name='ssl', checked=self.config.get('ajenti', 'ssl')=='1')
                ),
                UI.LayoutTableRow(
                    UI.Label(text='SSL certificate file:'),
                    UI.TextInput(name='cert_file', value=self.config.get('ajenti', 'cert_file'))
                ),
            )        
        p = UI.FormBox(o, id="frmGeneral")
        return p
        
    def get_ui_sec(self):
        tbl = UI.DataTable(
                UI.DataTableRow(
                    UI.DataTableCell(UI.Label(text='Login'), width='200px'),
                    UI.Label(),
                    header=True
                )  
              )
        for s in self.config.options('users'):
            tbl.appendChild(
                    UI.DataTableRow(
                        UI.Label(text=s),
                        UI.DataTableCell(
                            UI.MiniButton(text='Delete', id='deluser/'+s),
                            hidden=True
                        )
                    )
                )
        o = UI.VContainer(
                UI.Container(
                    UI.Checkbox(
                        text='HTTP Authorization', 
                        name='httpauth', 
                        checked=self.config.get('ajenti','auth_enabled')=='1'
                    )
                ),
                UI.Spacer(height=10),
                UI.Label(text='HTTP Accounts:', size='3'),
                tbl,
                UI.Button(text='Add new', id='adduser')
            )

        p = UI.VContainer(UI.FormBox(o, id="frmSecurity"))

        if self._adding_user:
            dlg = UI.DialogBox(
                      UI.LayoutTableRow(
                          UI.Label(text='Login: '),
                          UI.TextInput(name='login')
                      ),
                      UI.LayoutTableRow(
                          UI.Label(text='Password: '),
                          UI.TextInput(name='password')
                      ),
                      title='New user', id='dlgAddUser'  
                  )
            p.vnode(dlg)

        return p
        
    def hashpw(self, passw):
        return '{SHA}' + b64encode(sha1(passw).digest())
        
    @event('button/click')
    @event('minibutton/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'adduser':
            self._tab = 1
            self._adding_user = True
        if params[0] == 'deluser':
            self._tab = 1
            self.config.remove_option('users', params[1])
            self.config.save()
            
    @event('form/submit')
    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgAddUser':
            if vars.getvalue('action', '') == 'OK':
                self.config.set('users', vars.getvalue('login', ''), self.hashpw(vars.getvalue('password', '')))
                self.config.save()
            self._adding_user = False
        if params[0] == 'frmGeneral':
            self._tab = 0
            if vars.getvalue('action', '') == 'OK':
                self.config.set('ajenti', 'bind_host', vars.getvalue('bind_host', ''))
                self.config.set('ajenti', 'bind_port', vars.getvalue('bind_port', '8000'))
                self.config.set('ajenti', 'ssl', vars.getvalue('ssl', '0'))
                self.config.set('ajenti', 'cert_file', vars.getvalue('cert_file', ''))
            self.config.save()
        if params[0] == 'frmSecurity':
            self._tab = 1
            if vars.getvalue('action', '') == 'OK':
                self.config.set('ajenti', 'auth_enabled', vars.getvalue('httpauth', '0'))
            self.config.save()
            
