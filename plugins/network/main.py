from ajenti.ui import *
from ajenti.app.helpers import CategoryPlugin, ModuleContent
from api import *

class NetworkContent(ModuleContent):
    module = 'network'
    path = __file__

class NetworkPlugin(CategoryPlugin):
    text = 'Network'
    description = 'Configure adapters'
    icon = '/dl/network/icon.png'

    def on_session_start(self):
        self._status_text = ''

    def get_ui(self):
        net_config = self.app.grab_plugin(INetworkConfig)
        self._status_text = net_config.get_text()

    
        h = UI.HContainer(
                UI.Image(file='/dl/network/bigicon.png'),
                UI.Spacer(width=10),
                UI.VContainer(
                    UI.Label(text='Network', size=5),
                    UI.Label(text=self._status_text)
                )
            )
        return h
 
