from ajenti.ui import *
from ajenti.app.helpers import CategoryPlugin, ModuleContent

class NetworkContent(ModuleContent):
    module = 'network'
    path = __file__

class NetworkPlugin(CategoryPlugin):
    text = 'Network'
    description = 'Configure adapters'
    icon = '/dl/network/icon.png'

    def get_ui(self):
        return Image('/dl/network/icon.png')
