import subprocess

from jadi import component
from aj.plugins.services.api import ServiceManager, Service


@component(ServiceManager)
class SystemdServiceManager(ServiceManager):
    id = 'systemd'
    name = 'systemd'

    @classmethod
    def __verify__(cls):
        return subprocess.call(['which', 'systemctl']) == 0

    def __init__(self, context):
        pass

    def list(self, units=None):
        if not units:
            units = [x.split()[0] for x in subprocess.check_output(['systemctl', 'list-unit-files', '--no-legend', '--no-pager', '-la']).splitlines() if x]
            units = [x for x in units if x.endswith('.service') and '@' not in x]
            units = list(set(units))

        cmd = ['systemctl', 'show', '-o', 'json', '--full', '--all'] + units

        used_names = set()
        unit = {}
        for l in subprocess.check_output(cmd).splitlines() + [None]:
            if not l:
                if len(unit) > 0:
                    svc = Service(self)
                    svc.id = unit['Id']
                    svc.name, type = svc.id.rsplit('.', 1)

                    svc.name = svc.name.replace('\\x2d', '\x2d')
                    svc.running = unit['SubState'] == 'running'
                    svc.state = 'running' if svc.running else 'stopped'

                    if svc.name not in used_names:
                        yield svc

                    used_names.add(svc.name)
                unit = {}
            elif '=' in l:
                k, v = l.split('=', 1)
                unit[k] = v

    def get_service(self, _id):
        for s in self.list(units=[_id]):
            return s

    def start(self, _id):
        subprocess.check_call(['systemctl', 'start', _id], close_fds=True)

    def stop(self, _id):
        subprocess.check_call(['systemctl', 'stop', _id], close_fds=True)

    def restart(self, _id):
        subprocess.check_call(['systemctl', 'restart', _id], close_fds=True)
