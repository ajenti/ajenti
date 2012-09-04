from ajenti.ui import *
from ajenti import apis
from ajenti.com import implements, Plugin
from ajenti.api import *
from ajenti.utils import *
from ajenti import apis
from usage import DiskUsageMeter

class DiskUsageWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'Disk Usage'
    icon = '/dl/hddstat/icon.png'
    name = 'Disk Usage'
    style = 'normal'

    def get_ui(self, cfg, id=None):
        if cfg == None:
            cfg = "total"
        m = DiskUsageMeter(self.app).prepare(cfg)
        return UI.HContainer(
            UI.ProgressBar(value=m.get_value(cfg), max=m.get_max(), width=220),
            UI.Label(text=str('%s : %d %%' % (cfg,  m.get_value(cfg)))),
        )

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        mgr = self.app.get_backend(apis.services.IServiceManager)
        dlg = self.app.inflate('hddstat:widget-config')
        u = shell('df --total').split('\n')[1:-2];
        u.append ('total')
        for y in u:
            s = y.split()
            s = s.pop()
            dlg.append('list', UI.SelectOption(
                value=s,
                text=s,
            ))
        return dlg
   
 
    def process_config(self, vars):
        return vars.getvalue('svc', None)
