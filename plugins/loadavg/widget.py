from ajenti.ui import *
from ajenti.plugins.dashboard.api import *
from ajenti.com import implements, Plugin
from ajenti.app.helpers import *
from ajenti.utils import *


class LoadWidget(Plugin):
    implements(IDashboardWidget)

    def get_ui(self):
        w = UI.Widget(
                UI.HContainer(
                    UI.Image(file='/dl/loadavg/widget.png'),
                    UI.Label(text='System load:', bold=True),
                    UI.Label(text=self.get_load())
                )
            )
        return w

    def get_load(self):
        return ' / '.join(open('/proc/loadavg', 'r').read().split()[0:3])


class MemWidget(Plugin):
    implements(IDashboardWidget)

    def get_ui(self):
        ru, rt = self.get_ram()
        su, st = self.get_swap()
        w = UI.Widget(
                UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Image(file='/dl/loadavg/widget_mem.png'),
                        UI.Label(text='RAM:', bold=True),
                        UI.ProgressBar(value=ru, max=rt, width=100),
                        UI.Label(text="%sM / %sM"%(ru,rt)),
                        spacing=4
                    ),
                    UI.LayoutTableRow(
                        UI.Image(file='/dl/loadavg/widget_swap.png'),
                        UI.Label(text='Swap:', bold=True),
                        UI.ProgressBar(value=su, max=st, width=100) if int(st) != 0 else None,
                        UI.Label(text="%sM / %sM"%(ru,rt)),
                        spacing=4
                    )
                )
            )
        return w

    def get_ram(self):
        s = shell('free -m | grep Mem').split()[1:]
        t = int(s[0])
        u = int(s[1])
        b = int(s[4])
        c = int(s[5])
        u -= c + b;
        return (u, t)

    def get_swap(self):
        s = shell('free -m | grep Swap').split()[1:]
        return (int(s[1]), int(s[0]))


class LoadContent(ModuleContent):
    module = 'loadavg'
    path = __file__
