import gevent
import apt
import apt.cache
from apt.progress.base import AcquireProgress

from jadi import component
from aj.plugins.packages.api import PackageManager, Package


@component(PackageManager)
class APTPackageManager(PackageManager):
    id = 'apt'
    name = 'APT'

    def __init__(self, context):
        PackageManager.__init__(self, context)

    def __make_package(self, apt_package):
        p = Package(self)
        p.id = apt_package.fullname if hasattr(apt_package, 'fullname') else apt_package.name
        p.name = p.id
        v = apt_package.versions[-1]
        p.version = v.version
        p.description = v.summary
        p.is_installed = apt_package.installed is not None
        if p.is_installed:
            p.installed_version = apt_package.installed.version
            p.is_upgradeable = p.installed_version != p.version
        return p

    def list(self, query=None):
        cache = apt.Cache()
        for _id in cache.keys():
            yield self.__make_package(cache[_id])

    def get_package(self, _id):
        cache = apt.Cache()
        return self.__make_package(cache[_id])

    def update_lists(self, progress_callback):
        class Progress(AcquireProgress):
            def fetch(self, item):
                message = '%s%% %s' % (
                    int(100 * self.current_items / self.total_items),
                    item.shortdesc
                )
                progress_callback(message=message, done=self.current_items, total=self.total_items)

            def stop(self):
                self.done = True

        cache = apt.Cache()
        ack = Progress()
        try:
            cache.update(fetch_progress=ack)
        except apt.cache.FetchFailedException:
            pass

        while not hasattr(ack, 'done'):
            gevent.sleep(1)

    def get_apply_cmd(self, selection):
        cmd = 'apt-get install '
        for sel in selection:
            cmd += sel['package']['id'] + {
                'remove': '-',
                'install': '+',
                'upgrade': '+'
            }[sel['operation']] + ' '
        return cmd
