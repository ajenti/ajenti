import ajenti
from ajenti.api import *
from ajenti.ui import UIElement, p, on
from ajenti.ui.binder import Binder
from ajenti.plugins import BinaryDependency, ModuleDependency


@p('package', default='')
@p('text', default=_('This package can be installed automatically'))
@plugin
class PackageInstaller (UIElement, BasePlugin):
    typeid = 'packages:installer'

    def init(self):
        self.visible = False
        self.append(self.ui.inflate('packages:installer'))
        self.recheck()

    def on_page_load(self):
        self.recheck()

    def recheck(self):
        if ajenti.platform in db:
            apps = db[ajenti.platform]
            if self.package in apps:
                self.pkg = db[ajenti.platform][self.package]
                self.visible = True
                Binder(self, self).autodiscover().populate()
            if self.package.startswith('python-module-'):
                d = ModuleDependency(self.package[len('python-module-')])
            else:
                d = BinaryDependency(self.package)
            if d.satisfied():
                self.visible = False

    @on('install', 'click')
    def on_install(self):
        self.event('activate')
        self.context.launch('install-package', package=self.pkg)


db = {
    'debian': {
        'python-module-BeautifulSoup': 'python-beautifulsoup',
        'supervisord': 'supervisor',
        'hddtemp': 'hddtemp',
        'sensors': 'lm-sensors',
        'munin-cron': 'munin',
        'smbd': 'samba',
        'smartctl': 'smartmontools',
        'squid3': 'squid3',
        'apache2': 'apache2',
        'ctdb': 'ctdb',
        'mysql': 'mysql-server',
        'psql': 'postgresql',
        'nfsstat': 'nfs-kernel-server',
        'mdadm': 'mdadm',
        'nginx': 'nginx',
    },
    'centos': {
        'python-module-BeautifulSoup': 'python-BeautifulSoup',
        'supervisord': 'supervisor',
        'hddtemp': 'hddtemp',
        'sensors': 'lm_sensors',
        'munin-cron': 'munin',
        'smbd': 'samba',
        'smartctl': 'smartmontools',
        'squid3': 'squid',
        'apache2': 'httpd',
        'ctdb': 'ctdb',
        'mysql': 'mysql',
        'psql': 'postgresql',
        'mdadm': 'mdadm',
        'nginx': 'nginx',
    },
}
