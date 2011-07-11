from ajenti.api import *
from ajenti.ui import *
from ajenti.utils import hashpw
from ajenti.plugins.recovery.api import *


class ConfigPlugin(CategoryPlugin):
    text = 'Configure'
    icon = '/dl/config/icon.png'
    folder = 'bottom'

    def on_session_start(self):
        self._tab = 0
        self._adding_user = False
        self._config = None

    def get_ui(self):
        ui = self.app.inflate('config:main')

        ui.find('tabs').set('active', self._tab)

        # General
        ui.find('bind_host').set('value', self.app.gconfig.get('ajenti', 'bind_host'))
        ui.find('bind_port').set('value', self.app.gconfig.get('ajenti', 'bind_port'))
        ui.find('ssl').set('checked', self.app.gconfig.get('ajenti', 'ssl')=='1')
        ui.find('cert_file').set('value', self.app.gconfig.get('ajenti', 'cert_file'))

        # Security
        ui.find('httpauth').set('checked', self.app.gconfig.get('ajenti','auth_enabled')=='1')
        tbl = ui.find('accounts')
        for s in self.app.gconfig.options('users'):
            tbl.append(
                    UI.DataTableRow(
                        UI.Label(text=s),
                        UI.DataTableCell(
                            UI.MiniButton(text='Delete', id='deluser/'+s),
                            hidden=True
                        )
                    )
                )

        if not self._adding_user:
            ui.remove('dlgAddUser')

        # Configs
        cfgs = sorted(self.app.grab_plugins(IModuleConfig))
        t = ui.find('configs')
        for c in cfgs:
            if c.target:
                t.append(UI.DataTableRow(
                UI.Image(file=(None if not hasattr(c.target, 'icon') else c.target.icon)),
                UI.Label(text=(c.target.__name__ if not hasattr(c.target, 'text') else c.target.text)),
                UI.DataTableCell(
                    UI.MiniButton(text='Edit', id='editconfig/'+c.target.__name__),
                    hidden=True
                )
            ))

        if self._config:
            ui.append('main',
                self.app.get_config_by_classname(self._config).get_ui_edit()
            )

        return ui


    @event('button/click')
    @event('minibutton/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'adduser':
            self._tab = 1
            self._adding_user = True
        if params[0] == 'deluser':
            self._tab = 1
            self.app.gconfig.remove_option('users', params[1])
            self.app.gconfig.save()
        if params[0] == 'editconfig':
            self._tab = 2
            self._config = params[1]

    @event('form/submit')
    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgAddUser':
            self._tab = 1
            if vars.getvalue('action', '') == 'OK':
                self.app.gconfig.set('users', vars.getvalue('login', ''), hashpw(vars.getvalue('password', '')))
                self.app.gconfig.save()
            self._adding_user = False
        if params[0] == 'frmGeneral':
            self._tab = 0
            if vars.getvalue('action', '') == 'OK':
                self.app.gconfig.set('ajenti', 'bind_host', vars.getvalue('bind_host', ''))
                self.app.gconfig.set('ajenti', 'bind_port', vars.getvalue('bind_port', '8000'))
                self.app.gconfig.set('ajenti', 'ssl', vars.getvalue('ssl', '0'))
                self.app.gconfig.set('ajenti', 'cert_file', vars.getvalue('cert_file', ''))
                self.app.gconfig.save()
        if params[0] == 'frmSecurity':
            self._tab = 1
            if vars.getvalue('action', '') == 'OK':
                self.app.gconfig.set('ajenti', 'auth_enabled', vars.getvalue('httpauth', '0'))
                self.app.gconfig.save()
        if params[0] == 'dlgEditModuleConfig':
            if vars.getvalue('action','') == 'OK':
                cfg = self.app.get_config_by_classname(self._config)
                cfg.apply_vars(vars)
                cfg.save()
            self._config = None


class AjentiConfig (Plugin):
    implements (IConfigurable)
    name = 'Ajenti'
    icon = '/dl/core/ui/favicon.png'
    id = 'ajenti'
    _no_uzuri_ = True

    def list_files(self):
        return ['/etc/ajenti/*']
