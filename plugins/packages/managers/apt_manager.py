import gevent
import apt
import apt.cache
from apt.progress.base import AcquireProgress

from jadi import component
from aj.plugins.packages.api import PackageManager, Package


@component(PackageManager)
class APTPackageManager(PackageManager):
    """
    Manager to handle apt packages.
    """

    id = 'apt'
    name = 'APT'

    def __init__(self, context):
        PackageManager.__init__(self, context)

    def __make_package(self, apt_package):
        """
        Convert apt package object in package object.

        :param apt_package: Apt package object from apt module
        :type apt_package: Apt package object from apt module
        :return: Package object
        :rtype: Package object
        """

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
        """
        Generator for all packages.

        :param query: Search string
        :type query: string
        :return: Package object
        :rtype:Package object
        """

        cache = apt.Cache()
        for _id in cache.keys():
            yield self.__make_package(cache[_id])

    def get_package(self, _id):
        """
        Get package informations.

        :param _id: Package name
        :type _id: string
        :return: Package object
        :rtype: Package object
        """

        cache = apt.Cache()
        return self.__make_package(cache[_id])

    def update_lists(self, progress_callback):
        """
        Refresh list of packages.

        :param progress_callback: Callback function to follow progress
        :type progress_callback: function
        """

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
        """
        Prepare command to apply.

        :param selection: Dict of packages an actions
        :type selection: dict
        :return: Command for terminal use
        :rtype: string
        """

        cmd = 'apt-get install '
        for sel in selection:
            cmd += sel['package']['id'] + {
                'remove': '-',
                'install': '+',
                'upgrade': '+'
            }[sel['operation']] + ' '
        return cmd
