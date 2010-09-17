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

    def get_ui(self):
        cfg = Config()
        cfg.load('/etc/iptables.up.rules')
        print cfg.dump()
                
        panel = UI.PluginPanel(UI.Label(), title='IPTables Firewall', icon='/dl/firewall/icon.png')
        panel.append(self.get_default_ui())
        return panel

    def get_default_ui(self):
        return UI.FWChain(
                UI.FWRule(action='ACCEPT'),
                UI.FWRule(action='DROP'),
                UI.FWRule(action='REJECT'),
                UI.FWRule(action='MASQUERADE'),
                UI.FWRule(action='EXIT'),
                UI.FWRule(action='RUN'),
                UI.FWRule(action='LOG'),
                name="Test"
               )
               
    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        pass
        

class FirewallContent(ModuleContent):
    module = 'firewall'
    path = __file__
    widget_files = ['fw.xslt']
    css_files = ['fw.css']
