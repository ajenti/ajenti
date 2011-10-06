from ajenti.api import *
from ajenti.utils import *
from ajenti.ui import *
from ajenti.plugins.core.api import *
from ajenti import apis

from backend import *


class DnsMasqPlugin(apis.services.ServiceControlPlugin):
    text = 'Dnsmasq'
    icon = '/dl/dnsmasq/icon.png'
    folder = 'servers'
    service_name = 'dnsmasq'

    def on_init(self):
        self.backend = Backend(self.app)
        self.cfg = self.backend.get_config()

    def on_session_start(self):
        self._editing_host = None
        self._editing_domain = None

    def get_main_ui(self):
        if not self.backend.test():
            self.put_message('err', 'Dnsmasq config not found')
            return None

        ui = self.app.inflate('dnsmasq:main')

        for lease in self.backend.get_leases():
            row = UI.DTR(
                UI.Label(text=lease['mac']),
                UI.Label(text=lease['ip']),
                UI.Label(text=lease['host']),
            )
            ui.append('list', row)

        for host in self.cfg['dhcp-hosts']:
            row = UI.DTR(
                UI.Label(text=self.backend.find_mac(host).upper()),
                UI.Label(text=self.backend.str_ident(host['id'])),
                UI.Label(text=self.backend.find_ip(host)),
                UI.Label(text=self.backend.str_act(host['act'])),
                UI.HContainer(
                    UI.TipIcon(
                        id='editHost/%i' % self.cfg['dhcp-hosts'].index(host),
                        text='Edit',
                        icon='/dl/core/ui/stock/edit.png'
                    ),
                    UI.TipIcon(
                        id='deleteHost/%i' % self.cfg['dhcp-hosts'].index(host),
                        warning='Delete host rule',
                        text='Delete',
                        icon='/dl/core/ui/stock/delete.png'
                    ),
                ),
            )
            ui.append('hosts', row)

        for host in self.cfg['domains']:
            row = UI.DTR(
                UI.Label(text=host[0]),
                UI.Label(text=host[1]),
                UI.HContainer(
                    UI.TipIcon(
                        id='editDomain/%i' % self.cfg['domains'].index(host),
                        text='Edit',
                        icon='/dl/core/ui/stock/edit.png'
                    ),
                    UI.TipIcon(
                        id='deleteDomain/%i' % self.cfg['domains'].index(host),
                        warning='Delete DNS entry',
                        text='Delete',
                        icon='/dl/core/ui/stock/delete.png'
                    ),
                ),
            )
            ui.append('domains', row)

        if self._editing_host is not None:
            dlg = self.app.inflate('dnsmasq:edit-host')
            self.setup_host_dialog(dlg)
            ui.append('main', dlg)

        if self._editing_domain is not None:
            dlg = self.app.inflate('dnsmasq:edit-domain')
            self.setup_domain_dialog(dlg)
            ui.append('main', dlg)

        return ui

    def setup_host_dialog(self, dlg):
        if self._editing_host == -1:
            return

        h = self.cfg['dhcp-hosts'][self._editing_host]
        for x in h['id']:
            if x[0] == 'mac':
                dlg.find('id_mac').set('checked', True)
                dlg.find('id_mac_val').set('value', x[1])
            if x[0] == 'dhcpid':
                dlg.find('id_dhcp').set('checked', True)
                dlg.find('id_dhcp_val').set('value', x[1])
            if x[0] == 'name':
                dlg.find('id_name').set('checked', True)
                dlg.find('id_name_val').set('value', x[1])
        for x in h['act']:
            if x[0] == 'ip':
                dlg.find('act_ip').set('checked', True)
                dlg.find('act_ip_val').set('value', x[1])
            if x[0] == 'set':
                dlg.find('act_tag').set('checked', True)
                dlg.find('act_tag_val').set('value', x[1])
            if x[0] == 'ignore':
                dlg.find('act_ignore').set('checked', True)
            if x[0] == 'name':
                dlg.find('act_name').set('checked', True)
                dlg.find('act_name_val').set('value', x[1])
            if x[0] == 'time':
                dlg.find('time').set('value', x[1])

    def setup_domain_dialog(self, dlg):
        if self._editing_domain == -1:
            return

        x = self.cfg['domains'][self._editing_domain]
        dlg.find('hostname').set('value', x[0])
        dlg.find('addr').set('value', x[1])

    @event('button/click')
    @event('minibutton/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'btnAddHost':
            self._editing_host = -1
        if params[0] == 'btnAddDomain':
            self._editing_domain = -1
        if params[0] == 'editHost':
            self._editing_host = int(params[1])
        if params[0] == 'deleteHost':
            del self.cfg['dhcp-hosts'][int(params[1])]
        if params[0] == 'editDomain':
            self._editing_domain = int(params[1])
        if params[0] == 'deleteDomain':
            del self.cfg['domains'][int(params[1])]
        self.backend.save_config(self.cfg)

    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEditHost':
            if vars.getvalue('action', None) == 'OK':
                x = { 'id': [], 'act': [] }
                if vars.getvalue('id_mac', None) == '1':
                    x['id'].append(('mac', vars.getvalue('id_mac_val', None)))
                if vars.getvalue('id_dhcp', None) == '1':
                    x['id'].append(('dhcpid', vars.getvalue('id_dhcp_val', None)))
                if vars.getvalue('id_name', None) == '1':
                    x['id'].append(('name', vars.getvalue('id_name_val', None)))
                if vars.getvalue('act_ip', None) == '1':
                    x['act'].append(('ip', vars.getvalue('act_ip_val', None)))
                if vars.getvalue('act_ignore', None) == '1':
                    x['act'].append(('ignore', None))
                if vars.getvalue('act_tag', None) == '1':
                    x['act'].append(('set', vars.getvalue('act_tag_val', None)))
                if vars.getvalue('act_name', None) == '1':
                    x['act'].append(('name', vars.getvalue('act_name_val', None)))
                if vars.getvalue('time', '') != '':
                    x['act'].append(('time', vars.getvalue('time', None)))

                if self._editing_host != -1:
                    self.cfg['dhcp-hosts'][self._editing_host] = x
                else:
                    self.cfg['dhcp-hosts'].append(x)

                self.backend.save_config(self.cfg)
            self._editing_host = None
        if params[0] == 'dlgEditDomain':
            if vars.getvalue('action', None) == 'OK':
                hn = vars.getvalue('hostname', None)
                addr = vars.getvalue('addr', None)
                if (hn and addr):
                    x = (hn, addr)
                    if self._editing_domain != -1:
                        self.cfg['domains'][self._editing_domain] = x
                    else:
                        self.cfg['domains'].append(x)

                self.backend.save_config(self.cfg)
            self._editing_domain = None
