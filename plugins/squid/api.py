from ajenti.com import *
from ajenti.apis import API


class Squid(API):
    class IPluginPart(Interface):
        weight = 0
        title = ''

        def init(parent, self, cfg, tab):
            pass

        def get_ui(self):
            pass

        def on_click(self, event, params, vars=None):
            pass

        def on_submit(self, event, params, vars=None):
            pass
