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

            for unit in shell("systemctl --no-ask-password --full -t service list-unit-files --all --no-legend").splitlines():
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
            re_status = re.compile("^ActiveState=(.+)$")

            status = shell("systemctl --no-ask-password --property ActiveState show %s.service" % name)
            match = re_status.search(status)

            if not match or match.group(1) != "active":
                return 'stopped'
            else:
                return 'running'
        else:
            s = shell('/etc/rc.d/%s status' % name)
            return 'running' if 'running' in s else 'stopped'

    def start(self, name):
        if self.use_systemd:
            shell("systemctl --no-ask-password start %s.service" % name)
        else:
            shell('/etc/rc.d/%s start'.format(name))

    def stop(self, name):
        if self.use_systemd:
            shell("systemctl --no-ask-password stop %s.service" % name)
        else:
            shell('/etc/rc.d/%s stop'.format(name))

    def restart(self, name):
        if self.use_systemd:
            shell("systemctl --no-ask-password reload-or-restart %s.service" % name)
        else:
            shell('/etc/rc.d/%s restart' % name)
