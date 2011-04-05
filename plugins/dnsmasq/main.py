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
                )
            )
            ui.append('hosts', row)
            
        return ui
   
    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'progress':
            pass
            
