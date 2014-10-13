import ajenti
from ajenti.api import *
from ajenti.ui import UIElement, p, on
from ajenti.ui.binder import Binder
from ajenti.plugins import BinaryDependency, ModuleDependency


@p('package', default='')
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
        if not self.package:
            return
        if ajenti.platform in db:
            apps = db[ajenti.platform]
            if self.package in apps:
                self.pkg = db[ajenti.platform][self.package]
                self.visible = True
                Binder(self, self).populate()
            if self.package.startswith('python-module-'):
                d = ModuleDependency(self.package[len('python-module-'):])
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
        'mysqld_safe': 'mysql-server',
        'psql': 'postgresql',
        'nfsstat': 'nfs-kernel-server',
        'mdadm': 'mdadm',
        'nginx': 'nginx',
        'ipmitool': 'ipmitool',
        'rethinkdb': 'rethinkdb',
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
        'mysqld_safe': 'mysql-server',
        'psql': 'postgresql',
        'mdadm': 'mdadm',
        'nginx': 'nginx',
        'ipmitool': 'ipmitool',
        'cron': 'cronie',
        'rethinkdb': 'rethinkdb',
    },
    'mageia': {
        'python-module-BeautifulSoup': 'python-beautifulsoup',
        'supervisord': 'supervisor',
        'hddtemp': 'hddtemp',
        'sensors': 'lm_sensors',
        'munin-cron': 'munin',
        'smbd': 'samba',
        'smartctl': 'smartmontools',
        'squid3': 'squid',
        'apache2': 'apache',
        'ctdb': 'ctdb',
        'mysql': 'mariadb',
        'mysqld_safe': 'mariadb-core',
        'psql': 'postgresql',
        'mdadm': 'mdadm',
        'nginx': 'nginx',
        'ipmitool': 'ipmitool',
        'cron': 'cronie',
        'openvpn': 'openvpn',
        'memcached': 'memcached',
        'rethinkdb': 'rethinkdb',
    },
    'arch': {
        'python-module-BeautifulSoup': 'python2-beautifulsoup3',
        'supervisord': 'supervisor',
        'hddtemp': 'hddtemp',
        'sensors': 'lm_sensors',
        'munin-cron': 'munin',
        'smbd': 'samba',
        'smartctl': 'smartmontools',
        'squid3': 'squid',
        'apache2': 'apache',
        'mysql': 'mariadb-clients',
        'mysqld_safe': 'mariadb',
        'psql': 'postgresql',
        'mdadm': 'mdadm',
        'nginx': 'nginx',
        'apcaccess': 'apcupsd',
        'openvpn': 'openvpn',
        'nsd': 'nsd',
        'memcached': 'memcached',
        'nfsstat': 'nfs-utils',
        'dhcpd': 'dhcp',
        'named': 'bind',
        'ipmitool': 'ipmitool',
        'rethinkdb': 'rethinkdb',
    },
}
