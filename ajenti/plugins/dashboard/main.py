import platform

from api import *

from ajenti.com import Interface
from ajenti.ui import *
from ajenti import version
from ajenti.utils import detect_distro
from ajenti.app.helpers import CategoryPlugin

class Dashboard(CategoryPlugin):

    text = 'Dashboard'
    description = 'Dashboard overview'
    icon = '/dl/dashboard/icon.png'

    widgets = Interface(IDashboardWidget)
    
    def get_ui(self):
        h = UI.HContainer(
                UI.Image(file='/dl/dashboard/server.png'),
                UI.Spacer(width=10),
                UI.VContainer(
                    UI.Label(text=platform.node(), size=5),
                    UI.Label(text='Ajenti ' + version),
                    UI.Label(text=detect_distro())
                ),
                width="100%"
            )
            
        w = UI.VContainer()
        for x in self.widgets:
            w.appendChild(x.get_ui())

        u = UI.VContainer(h, UI.Spacer(height=30), w, width="100%")
        return u
