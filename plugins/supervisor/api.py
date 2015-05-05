from supervisor.options import ClientOptions

from jadi import component
from aj.plugins.services.api import ServiceManager, Service, ServiceOperationError


@component(ServiceManager)
class SupervisorServiceManager(ServiceManager):
    id = 'supervisor'
    name = 'Supervisor'

    def __init__(self, context):
        options = ClientOptions()
        options.realize([])
        self.supervisor = options.getServerProxy().supervisor

    def list(self):
        for info in self.supervisor.getAllProcessInfo():
            yield self.__make_service(info)

    def __make_service(self, info):
        svc = Service(self)
        svc.id = info['name']
        svc.name = info['name']
        svc.state = info['statename']
        svc.running = svc.state == 'RUNNING'
        return svc

    def get_service(self, _id):
        return self.__make_service(self.supervisor.getProcessInfo(_id))

    def start(self, _id):
        if not self.supervisor.startProcess(_id):
            raise ServiceOperationError('Supervisor operation failed')

    def stop(self, _id):
        if not self.supervisor.stopProcess(_id):
            raise ServiceOperationError('Supervisor operation failed')

    def restart(self, _id):
        self.stop(_id)
        self.start(_id)
