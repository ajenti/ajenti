import os
import re
import subprocess

from ajenti.com import *
from ajenti.utils import *
from ajenti import apis

def _new_service(name, mgr):
  service = apis.services.Service()
  service.name = name
  service.mgr = mgr
  return service

class ArchSysVServiceManagerBackend:
    def list_all(self):
        services = []
        for service_name in os.listdir('/etc/rc.d'):
            services.append(_new_service(service_name, self))
        return sorted(services, key=lambda service: service.name)

    def get_status(self, name):
        running = os.listdir('/var/run/daemons')
        return 'running' if name in running else 'stopped'

    def start(self, name):
        shell('/etc/rc.d/' + name + ' start')

    def stop(self, name):
        shell('/etc/rc.d/' + name + ' stop')

    def restart(self, name):
        shell('/etc/rc.d/' + name + ' restart')

class ArchSystemdServiceManagerBackend:
    def list_all(self):
        systemd_command = 'systemctl --all --full --type=service ' + \
                          '--no-legend --no-pager list-units'
        service_pattern = re.compile('^(?P<name>.+)\.service.*$')

        services = []
        for line in shell(systemd_command).splitlines():
            name = service_pattern.match(line).group('name')
            services.append(_new_service(name, self))
        return sorted(services, key=lambda service: service.name)

    def get_status(self, name):
        systemd_command = 'systemctl --property=ActiveState ' + \
                          'show %s.service' % name
        status_pattern = re.compile('^ActiveState=(?P<status>.+)$')
        status = status_pattern.match(shell(systemd_command)).group('status')
        return 'running' if 'active' == status else 'stopped'

    def start(self, name):
        shell('systemctl start %s.service' % name)

    def stop(self, name):
        shell('systemctl stop %s.service' % name)

    def restart(self, name):
        shell('systemctl restart %s.service' % name)

class ArchServiceManager(Plugin):
    implements(apis.services.IServiceManager)
    platform = ['arch']

    def __init__(self):
        systemd_disabled = subprocess.call('systemctl')
        if systemd_disabled:
            self._backend = ArchSysVServiceManagerBackend()
        else:
            self._backend = ArchSystemdServiceManagerBackend()

    def list_all(self):
        return self._backend.list_all()

    def get_status(self, name):
        return self._backend.get_status(name)

    def start(self, name):
        self._backend.start(name)

    def stop(self, name):
        self._backend.stop(name)

    def restart(self, name):
        self._backend.restart(name)
