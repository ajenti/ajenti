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
        
    def get_main_ui(self):
        ui = self.app.inflate('dnsmasq:main')
        
        for lease in self.backend.get_leases():
            row = UI.DataTableRow(
                UI.Label(text=lease['mac']),
                UI.Label(text=lease['ip']),
                UI.Label(text=lease['host']),
            )
            ui.append('list', row)

        for host in self.cfg['dhcp-hosts']:
            row = UI.DataTableRow(
                UI.Label(text=self.backend.find_mac(host)),
                UI.Label(text=self.backend.str_ident(host['id'])),
                UI.Label(text=self.backend.find_ip(host)),
                UI.Label(text=self.backend.str_act(host['act'])),
                UI.DataTableCell(
                    UI.HContainer(
                        UI.MiniButton(
                            id='editHost/%i' % self.cfg['dhcp-hosts'].index(host),
                            text='Edit',
                        ),
                        UI.WarningMiniButton(
                            id='deleteHost/%i' % self.cfg['dhcp-hosts'].index(host),
                            msg='Delete host rule',
                            text='Delete',
                        ),
                    ),
                    hidden=True
                )
            )
            ui.append('hosts', row)
            
        if self._editing_host is not None:
            dlg = self.app.inflate('dnsmasq:edit-host')
            self.setup_host_dialog(dlg)
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
        
    @event('button/click')
    @event('minibutton/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'btnAddHost':
            self._editing_host = -1
        if params[0] == 'editHost':
            self._editing_host = int(params[1])
        if params[0] == 'deleteHost':
            del self.cfg['dhcp-hosts'][int(params[1])]
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
            
