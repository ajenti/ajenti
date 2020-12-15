import logging
import dnf
import dnf.cli
from dnf.sack import _rpmdb_sack
import time
import re

from jadi import component
from aj.plugins.packages.api import PackageManager, Package

@component(PackageManager)
class DNFPackageManager(PackageManager):
    id = 'dnf'
    name = 'DNF'

    @classmethod
    def __verify__(cls):
        try:
            dnf.Base()
            logging.error('Package manager DNF found')
            return True
        except Exception as e:
            return False

    def __init__(self, context):
        PackageManager.__init__(self, context)
        self.dnf = dnf.Base()
        self.dnf.read_all_repos()
        self.dnf.fill_sack()
        q = self.dnf.sack.query()
        self.installed_packages = q.installed()
        self.available_packages = q.available()
        self.available_packages = self.available_packages.union(self.installed_packages)

    def __make_package(self, pkg, pkg_is_installed=False):

        p = Package(self)
        p.id = '%s.%s' % (pkg.name, pkg.arch)

        p.name = pkg.name
        p.ver = re.sub("[^0-9]", "", pkg.version)
        p.rel = re.sub("[^0-9]", "", pkg.release)

        sversion = (pkg.version+'-'+ pkg.release)
        p.version = (p.ver + p.rel)
        p.description = pkg.summary 
        p.is_installed = pkg_is_installed
        p.is_upgradeable = False

        if p.is_installed:

            for apkg in (self.available_packages.filter(name=pkg.name) or [None]):
                apgk_version = ""
        
                if apkg:
                    apkg_version = '%s%s' % (re.sub("[^0-9]", "", apkg.version), re.sub("[^0-9]", "", apkg.release))

                p.is_upgradeable = int(apkg_version) > int(p.version) if apkg_version else False
                if p.is_upgradeable:
                    #p.is_installed = False
                    break

        p.version = sversion
        return p

    def list(self, query=None):
        print (" ::: 1")
#        time.sleep(1)
        w = [str(x) for x in self.installed_packages]
        for pkg in self.available_packages:
            if pkg.installed or str(pkg) not in w:
                yield self.__make_package(pkg, pkg.installed)

    def get_package(self, _id):
        pkg = (self.available_packages.filter(names=[_id]) or [None])[0]
#        print ('GET', _id, 'PK',pkg)
        return self.__make_package(pkg)

    def update_lists(self, progress_callback):
        class Progress():
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
        progress = dnf.cli.progress.MultiFileProgressMeter()
        y = dnf.Base()
        #dnf.download_packages(dnf.transaction.install_set, progress)
        y.read_all_repos()
        y.repos.update()
        y.update_cache()

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
            cmd += 'dnf3 install ' + ' '.join(to_install)
            if len(to_remove) > 0:
                cmd += ' && '
        if len(to_remove) > 0:
            cmd += 'dnf3 remove ' + ' '.join(to_remove)
        return cmd
