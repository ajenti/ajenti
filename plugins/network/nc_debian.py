from ajenti.com import *
from api import *

class DebianNetworkConfig(Plugin):
    implements(INetworkConfig)

    interfaces = None
    
    def get_text(self): return 'debian!'
