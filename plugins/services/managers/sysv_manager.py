import os
import subprocess

from jadi import component
from aj.plugins.services.api import ServiceManager, Service


INIT_D = '/etc/init.d'
UPSTART_PATTERN = '/etc/init/%s.conf'


@component(ServiceManager)
class SysVServiceManager(ServiceManager):
    id = 'sysv'
    name = 'System V'

    @classmethod
    def __verify__(cls):
        return os.path.exists(INIT_D)

    def __init__(self, context):
        pass

    def list(self):
        for _id in os.listdir(INIT_D):
            path = os.path.join(INIT_D, _id)
            if _id.startswith('.'):
                continue
            if _id.startswith('rc'):
                continue
            if os.path.islink(path):
                continue
            if os.path.exists(UPSTART_PATTERN % _id):
                continue
            yield self.get_service(_id)

    def get_service(self, _id):
        svc = Service(self)
        svc.id = svc.name = _id
        try:
            svc.running = self._run_action(_id, 'status')
            svc.state = 'running' if svc.running else 'stopped'
        except:
            svc.running = False
        return svc

    def _run_action(self, _id, action):
        return subprocess.call([os.path.join(INIT_D, _id), action], close_fds=True) == 0

    def start(self, _id):
        self._run_action(_id, 'start')

    def stop(self, _id):
        self._run_action(_id, 'stop')

    def restart(self, _id):
        self._run_action(_id, 'restart')
