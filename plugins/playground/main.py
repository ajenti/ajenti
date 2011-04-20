from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import shell, enquote, BackgroundProcess
from ajenti.plugins.core.api import *
from ajenti.utils import *

import sys


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
        if params[0] == 'progress':
            PlaygroundProgress(self.app).start()
        if params[0] == 'btnExit':
            self.app.stop()
            
            
class PlaygroundProgress(SessionPlugin):
    implements(IProgressBoxProvider)
    title = 'Playground'
    icon = '/dl/playground/icon.png'
    can_abort = True
    
    def on_session_start(self):
        self._w = False
        
    def start(self): self._w = True

    def has_progress(self):  
        return self._w
        
    def get_progress(self):
        return 'Working'
    
    def abort(self):
        self._w = False
                            
