from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import *

from backend import *


class FirewallPlugin(CategoryPlugin):
    text = 'Firewall'
    icon = '/dl/firewall/icon_small.png'
    folder = 'system'

    def on_init(self):
        self.cfg = Config()
        self.cfg.load('/etc/iptables.up.rules')

    def get_ui(self):
        panel = UI.PluginPanel(UI.Label(), title='IPTables Firewall', icon='/dl/firewall/icon.png')
        panel.append(self.get_default_ui())
        return panel

    def get_default_ui(self):
        ui = UI.VContainer(spacing=15)
        for t in self.cfg.tables:
            t = self.cfg.tables[t]
            for ch in t.chains:
                ch = t.chains[ch]
                uic = UI.FWChain(tname=t.name, name=ch.name, default=ch.default)
                for r in ch.rules:
                    uic.append(UI.FWRule(action=r.action, desc=r.raw))
                ui.append(uic)
            ui.append(UI.Button(text='Add new chain to '+t.name, id='addchain/'+t.name))
        return ui
               
    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'setdefault':
            self.cfg.tables[params[1]].chains[params[2]].default = params[3]
            self.cfg.save('/etc/iptables.up.rules')
        

class FirewallContent(ModuleContent):
    module = 'firewall'
    path = __file__
    widget_files = ['fw.xslt']
    css_files = ['fw.css']
