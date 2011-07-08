from ajenti.ui import *
from ajenti.plugins.dashboard.api import *
from ajenti.com import implements, Plugin
from ajenti.api import *
from ajenti import apis


class LoadWidget(Plugin):
    implements(IDashboardWidget)
    title = 'System load'
    icon = '/dl/sysload/widget.png'
    name = 'System load'
    style = 'linear'
    
    def get_ui(self, cfg, id=None):
        stat = self.app.get_backend(apis.sysstat.ISysStat)
        ui = self.app.inflate('sysload:load')
        load = stat.get_load()
        ui.find('1m').set('text', load[0])
        ui.find('5m').set('text', load[1])
        ui.find('15m').set('text', load[2])
        return ui
    
    def handle(self, event, params, cfg, vars=None):
        pass
    
    def get_config_dialog(self):
        return None
        
    def process_config(self, event, params, vars):
        pass
                    

class RamWidget(Plugin):
    implements(IDashboardWidget)
    title = 'RAM'
    icon = '/dl/sysload/widget_mem.png'
    name = 'Memory'
    style = 'normal'
        
    def get_ui(self, cfg, id=None):
        stat = self.app.get_backend(apis.sysstat.ISysStat)
        ru, rt = stat.get_ram()
        return UI.HContainer(
            UI.ProgressBar(value=ru, max=rt, width=220),
            UI.Label(text="%sM / %sM"%(ru,rt)),
        )
        
        su, st = stat.get_swap()
        w = UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Image(file='/dl/sysload/widget_mem.png'),
                        UI.Label(text='RAM:', bold=True),
                        spacing=4
                    ),
                    UI.LayoutTableRow(
                        UI.Image(file='/dl/sysload/widget_swap.png'),
                        UI.Label(text='Swap:', bold=True),
                        UI.ProgressBar(value=su, max=st, width=100) if int(st) != 0 else None,
                        UI.Label(text="%sM / %sM"%(su,st)),
                        spacing=4
                    )
            )
        return w
        
    def handle(self, event, params, cfg, vars=None):
        pass
    
    def get_config_dialog(self):
        return None
        
    def process_config(self, vars):
        pass
                        
                        
class SwapWidget(Plugin):
    implements(IDashboardWidget)
    title = 'Swap'
    icon = '/dl/sysload/widget_swap.png'
    name = 'Swap'
    style = 'normal'
        
    def get_ui(self, cfg, id=None):
        stat = self.app.get_backend(apis.sysstat.ISysStat)
        su, st = stat.get_swap()
        return UI.HContainer(
            UI.ProgressBar(value=su, max=int(st)+1, width=220),
            UI.Label(text="%sM / %sM"%(su,st)),
        )
        
    def handle(self, event, params, cfg, vars=None):
        pass
    
    def get_config_dialog(self):
        return None
        
    def process_config(self, vars):
        pass
                                           
