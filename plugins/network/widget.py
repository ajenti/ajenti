from ajenti.ui import *
from ajenti.plugins.dashboard.api import *
from ajenti.com import implements, Plugin
from api import *


class NetworkWidget(Plugin):
    implements(IDashboardWidget)

    def get_ui(self):
        cfg = self.app.get_backend(INetworkConfig)
        t = UI.LayoutTable()
        w = UI.Widget(t)
        
        for x in cfg.interfaces:
            i = cfg.interfaces[x]
            t.append(UI.LayoutTableRow(
                    UI.Image(file='/dl/network/%s.png'%('up' if i.up else 'down')),
                    UI.Label(text=i.name),
                    UI.Label(text=i.addr),
                    spacing=4
                ))
                
        return w
