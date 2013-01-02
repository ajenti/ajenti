import os
import re

from ajenti.com import *
from ajenti.utils import *
from ajenti import apis


class ArchServiceManager(Plugin):
    implements(apis.services.IServiceManager)
    platform = ['arch']

    def __init__(self):
        self.use_systemd = os.path.realpath("/proc/1/exe").endswith("/systemd")

    def list_all(self):
        services = []

        if self.use_systemd:
            service = re.compile("^([^\s]+)\.service\W")

            for unit in shell("systemctl --no-ask-password --full -t service list-unit-files --all").splitlines():
                match = service.match(unit)
                if match:
                    services.append(match.group(1))
        else:
            services = os.listdir('/etc/rc.d')

        r = []
        for s in services:
            svc = apis.services.Service()
            svc.name = s
            svc.mgr = self
            r.append(svc)

        return sorted(r, key=lambda s: s.name)

    def get_status(self, name):
        if self.use_systemd:
            re_status = re.compile("^\s+Active: ([^\s]+)", re.M)

            status = shell("systemctl --no-ask-password status {}.service".format(name))
            match = re_status.search(status)

            if not match or match.group(1) != "active":
                return 'stopped'
            else:
                return 'running'
        else:
            s = shell('/etc/rc.d/{} status'.format(name))
            return 'running' if 'running' in s else 'stopped'

    def start(self, name):
        if self.use_systemd:
            shell("systemctl --no-ask-password start {}.service".format(name))
        else:
            shell('/etc/rc.d/{} start'.format(name))

    def stop(self, name):
        if self.use_systemd:
            shell("systemctl --no-ask-password stop {}.service".format(name))
        else:
            shell('/etc/rc.d/{} stop'.format(name))

    def restart(self, name):
        if self.use_systemd:
            shell("systemctl --no-ask-password reload-or-restart {}.service".format(name))
        else:
            shell('/etc/rc.d/{} restart'.format(name))
