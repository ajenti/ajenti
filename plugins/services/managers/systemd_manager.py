import logging
import subprocess

from aj.api import *
from aj.plugins.services.api import ServiceManager, Service


@component(ServiceManager)
class SystemdServiceManager (ServiceManager):
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
            service = Service(self)
            service.id, load_state, active_state, sub_state, name = tokens
            service.name, type = service.id.rsplit('.', 1)
            service.name = service.name.replace('\\x2d', '\x2d')
            if type != 'service':
                continue
            service.running = sub_state == 'running'
            service.state = 'running' if service.running else 'stopped'
            yield service

    def get(self, id):
        for s in self.list():
            if s.id == id:
                return s

    def start(self, id):
        subprocess.check_call(['systemctl', 'start', id], close_fds=True)

    def stop(self, id):
        subprocess.check_call(['systemctl', 'stop', id], close_fds=True)

    def restart(self, id):
        subprocess.check_call(['systemctl', 'restart', id], close_fds=True)
