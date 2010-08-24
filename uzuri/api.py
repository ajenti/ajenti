from ajenti.com import *
from ajenti.app.helpers import CategoryPlugin
from ajenti.app.api import IHeaderProvider

class IClusteredPlugin(Interface):
    pass

class ClusteredPlugin(CategoryPlugin):
    implements(IClusteredPlugin, IHeaderProvider)
    abstract = True

    uzuri_success = True

    def clustering_success(self, s):
        self.uzuri_success = s

    def get_headers(self):
        return [
            ('X-Uzuri-Success', '1' if self.uzuri_success else '0'),
            ('X-Uzuri-Plugin', self.get_name())
        ]
