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
                )
            )
            
        w = UI.LayoutTable(width="600px")
        for i in range(0, len(self.widgets)/2):
            x = self.widgets[i*2]
            y = self.widgets[i*2+1]
            w.appendChild(UI.LayoutTableRow(
                                UI.LayoutTableCell(x.get_ui(), width="300px"),
                                UI.LayoutTableCell(y.get_ui(), width="300px")
                          )
              )

        if len(self.widgets) % 2 == 1:
            w.appendChild(UI.LayoutTableRow(
                                UI.LayoutTableCell(self.widgets[len(self.widgets)-1].get_ui(), width="300px"),
                                UI.LayoutTableCell(width="300px")
                          )
              )
        
        u = UI.VContainer(h, UI.Spacer(height=30), w)
        return u
