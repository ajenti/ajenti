import yum

from jadi import component
from aj.plugins.packages.api import PackageManager, Package


@component(PackageManager)
class YUMPackageManager(PackageManager):
    id = 'yum'
    name = 'YUM'

    @classmethod
    def __verify__(cls):
        try:
            yum.YumBase().doGenericSetup(cache=1)
            return True
        except:
            return False

    def __init__(self, context):
        PackageManager.__init__(self, context)
        self.yum = yum.YumBase()
        self.yum.doGenericSetup(cache=1)

    def __make_package(self, pkg):
        pkg_installed = (self.yum.rpmdb.searchNames(names=[pkg.name]) or [None])[0]
        p = Package(self)
        p.id = '%s.%s' % (pkg.name, pkg.arch)
        p.name = pkg.name
        p.version = pkg.version
        p.description = pkg.arch  # nothing better
        p.is_installed = pkg_installed is not None
        if p.is_installed:
            p.installed_version = pkg_installed.version
            p.is_upgradeable = p.installed_version != p.version
        return p

    def list(self, query=None):
        for pkg in self.yum.pkgSack.returnPackages():
            yield self.__make_package(pkg)

    def get_package(self, _id):
        pkg = (self.yum.searchNames(names=[_id]) or [None])[0]
        return self.__make_package(pkg)

    def update_lists(self, progress_callback):
        class Progress(object):
            def __init__(self):
                self.size = 0
                self.done = 0
                self.name = None

            def end(self, amount_read, now=None):
                pass

            def start(self, filename=None, url=None, basename=None, size=None, now=None, text=None):
                self.size = size
                self.done = 0
                self.name = url

            def update(self, amount_read, now=None):
                self.done = amount_read
                message = '%s%% %s' % (int(100 * self.done / self.size), self.name)
                progress_callback(message=message, done=self.done, total=self.size)

        progress_callback(message='Preparing')
        y = yum.YumBase()
        y.repos.setProgressBar(Progress())
        y.cleanMetadata()
        y.repos.doSetup()
        y.repos.populateSack()

    def get_apply_cmd(self, selection):
        to_install = [
            sel['package']['id']
            for sel in selection
            if sel['operation'] in ['install', 'upgrade']
        ]
        to_remove = [
            sel['package']['id']
            for sel in selection
            if sel['operation'] == 'remove'
        ]
        cmd = ''
        if len(to_install) > 0:
            cmd += 'yum install ' + ' '.join(to_install)
            if len(to_remove) > 0:
                cmd += ' && '
        if len(to_remove) > 0:
            cmd += 'yum remove ' + ' '.join(to_remove)
        return cmd
