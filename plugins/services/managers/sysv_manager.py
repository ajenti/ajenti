import os
import subprocess

from aj.api import *
from aj.plugins.services.api import ServiceManager, Service


INIT_D = '/etc/init.d'
UPSTART_PATTERN = '/etc/init/%s.conf'


@component(ServiceManager)
class SysVServiceManager (ServiceManager):
    id = 'sysv'
    name = 'System V'

    @classmethod
    def __verify__(cls):
        return os.path.exists(INIT_D)

    def __init__(self, context):
        pass

    def list(self):
        for id in os.listdir(INIT_D):
            path = os.path.join(INIT_D, id)
            if id.startswith('.'):
                continue
            if id.startswith('rc'):
                continue
            if os.path.islink(path):
                continue
            if os.path.exists(UPSTART_PATTERN % id):
                continue
            yield self.get(id)

    def get(self, id):
        service = Service(self)
        service.id = service.name = id
        try:
            service.running = self._run_action(id, 'status')
            service.state = 'running' if service.running else 'stopped'
        except:
            service.running = False
        return service

    def _run_action(self, id, action):
        return subprocess.call([os.path.join(INIT_D, id), action], close_fds=True) == 0

    def start(self, id):
        self._run_action(id, 'start')

    def stop(self, id):
        self._run_action(id, 'stop')

    def restart(self, id):
        self._run_action(id, 'restart')
