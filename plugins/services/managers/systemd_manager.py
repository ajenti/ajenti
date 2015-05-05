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

    def list(self):
        for l in subprocess.check_output(['systemctl', 'list-units', '-la']).splitlines()[1:]:
            if not l:
                break
            tokens = l.split(None, 4)
            if len(tokens) != 5:
                continue
            svc = Service(self)
            svc.id, load_state, active_state, sub_state, name = tokens
            svc.name, type = svc.id.rsplit('.', 1)
            svc.name = svc.name.replace('\\x2d', '\x2d')
            if type != 'svc':
                continue
            svc.running = sub_state == 'running'
            svc.state = 'running' if svc.running else 'stopped'
            yield svc

    def get_service(self, _id):
        for s in self.list():
            if s.id == _id:
                return s

    def start(self, _id):
        subprocess.check_call(['systemctl', 'start', _id], close_fds=True)

    def stop(self, _id):
        subprocess.check_call(['systemctl', 'stop', _id], close_fds=True)

    def restart(self, _id):
        subprocess.check_call(['systemctl', 'restart', _id], close_fds=True)
