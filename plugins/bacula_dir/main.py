from ajenti.api import *
from ajenti.utils import *
from ajenti.ui import *
from ajenti.plugins.core.api import *
from ajenti import apis

from backend import *


class BaculaDirPlugin(apis.services.ServiceControlPlugin):
    text = 'Bacula Director'
    icon = '/dl/bacula_dir/icon.png'
    folder = 'apps'
    service_name = 'bacula-director'

    def on_init(self):
        self.dir = Director(self.app) 
        
    def get_main_ui(self):
        ui = self.app.inflate('bacula_dir:main')
        st = self.dir.get_status()
        print st
        return ui
   
    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'msgInfo':
            r = apis.bacula.query('status director')
            self.put_message('info', r)
        if params[0] == 'msgWarn':
            self.put_message('warn', 'Warning')
        if params[0] == 'msgErr':
            self.put_message('err', 'Error')
        if params[0] == 'progress':
            PlaygroundProgress(self.app).start()
            
