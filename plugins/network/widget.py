from ajenti.ui import *
from ajenti.plugins.dashboard.api import *
from ajenti.com import implements, Plugin
from api import *


class NetworkWidget(Plugin):
    implements(IDashboardWidget)
    title = 'Networking'
    
    def get_ui(self):
        cfg = self.app.get_backend(INetworkConfig)
        w = UI.LayoutTable()
        
        for x in cfg.interfaces:
            i = cfg.interfaces[x]
            w.append(UI.LayoutTableRow(
                    UI.Image(file='/dl/network/%s.png'%('up' if i.up else 'down')),
                    UI.Label(text=i.name),
                    UI.Label(text=cfg.get_ip(i)),
                    spacing=4
                ))
                
        return w
