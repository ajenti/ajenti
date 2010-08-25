from hashlib import sha1
from base64 import b64encode

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
            ('x-uzuri-success', '1' if self.uzuri_success else '0'),
            ('x-uzuri-plugin', self.get_name()),
            ('x-uzuri-config-hash', b64encode(sha1(self.get_configuration_string()).digest()))
        ]

    def get_configuration_string(self):
        return ""
