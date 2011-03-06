from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import shell, enquote, BackgroundProcess
from ajenti.plugins.core.api import *
from ajenti.utils import *


class PlaygroundPlugin(CategoryPlugin):
    text = 'Playground'
    icon = '/dl/playground/icon.png'
    folder = 'apps'

    def get_ui(self):
        ui = self.app.inflate('playground:main')
        return ui
   
    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'msgInfo':
            self.put_message('info', 'Information')
        if params[0] == 'msgWarn':
            self.put_message('warn', 'Warning')
        if params[0] == 'msgErr':
            self.put_message('err', 'Error')
            
            
