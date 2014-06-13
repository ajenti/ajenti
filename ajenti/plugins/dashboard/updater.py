import gevent

from ajenti.api import *
from ajenti.plugins.packages.api import PackageManager, PackageInfo


@plugin
class AjentiUpdater (BasePlugin):
    AJENTI_PACKAGE_NAME = 'ajenti'

    def run_update(self, packages):
        packages = packages or [self.AJENTI_PACKAGE_NAME]
        actions = []
        for name in packages:
            mgr = PackageManager.get()
            p = PackageInfo()
            p.name, p.action = name, 'i'
            actions.append(p)
        mgr.do(actions)

    def check_for_updates(self, callback):
        try:
            mgr = PackageManager.get()
        except NoImplementationsError:
            return

        def worker():
            mgr.refresh()
            r = []
            for p in mgr.upgradeable:
                if p.name.startswith(self.AJENTI_PACKAGE_NAME):
                    r.append(p.name)
            callback(r)

        gevent.spawn(worker)
