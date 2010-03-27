from ajenti.com import *
from api import *

class UbuntuNetworkConfig(Plugin):
    implements(INetworkConfig)

    def get_text(self): return 'ubuntu!'
