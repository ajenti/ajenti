import platform

from ajenti.com import Interface
from ajenti.ui import *
from ajenti import version
from ajenti.utils import detect_distro
from ajenti.app.helpers import CategoryPlugin, ModuleContent

from api import *


class Dashboard(CategoryPlugin):
    text = 'Dashboard'
    icon = '/dl/dashboard/icon.png'
    folder = 'top'

    widgets = Interface(IDashboardWidget)

    def get_ui(self):
        # Arrange widgets in two columns
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

        u = UI.PluginPanel(UI.Label(text=detect_distro()), w, title=platform.node(), icon='/dl/dashboard/server.png')
        return u


class DashboardContent(ModuleContent):
    path = __file__
    module = 'dashboard'
    css_files = ['widget.css']
    widget_files = ['widgets.xml']
