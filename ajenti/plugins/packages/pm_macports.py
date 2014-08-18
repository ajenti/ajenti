from ajenti.api import *
from api import PackageInfo, PackageManager


@plugin
@rootcontext
@persistent
class MacPortsPackageManager (PackageManager):
    platforms = ['osx']

    def init(self):
        self.upgradeable = []

    def get_lists(self):
        pass

    def refresh(self):
        pass

    def search(self, query):
        return []

    def do(self, actions):
        pass
