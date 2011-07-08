from ajenti.com import Interface


class IDashboardWidget(Interface):
    title = ''
    name = ''
    icon = ''
    style = 'normal'
    
    def get_ui(self, cfg, id=None):
        pass

    def handle(self, event, params, cfg, vars=None):
        pass
    
    def get_config_dialog(self):
        pass
        
    def process_config(self, vars):
        pass
        
