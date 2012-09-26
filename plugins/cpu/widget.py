from ajenti.ui import *
from ajenti import apis
from ajenti.com import implements, Plugin
from ajenti.api import *
from ajenti.utils import *
from ajenti import apis
from cpu import Cpu

class CpuWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'CPU Usage'
    icon = '/dl/cpu/icon.png'
    name = 'CPU Usage'
    style = 'normal'

    def get_ui(self, cfg, id=None):
        m = Cpu(self.app).prepare(cfg)
        return UI.HContainer(
            UI.ProgressBar(value=m.get_value(), max=m.get_max(), width=220),
            UI.Label(text=str(m.get_value())+'%'),
        )

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        return None
    
    def process_config(self, vars):
        pass
