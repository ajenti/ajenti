from ajenti.ui import *
from ajenti.com import *


class IProgressBoxProvider(Interface):
    icon = ""
    title = ""
    
    def has_progress(self):
        return False
        
    def get_progress(self):
        return ''
        
    def abort(self):
        pass