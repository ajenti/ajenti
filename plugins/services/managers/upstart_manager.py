from dbus.exceptions import DBusException
from upstart.system import UpstartSystem, DirectUpstartBus
from upstart.job import UpstartJob

from jadi import component
from aj.plugins.services.api import ServiceManager, Service, ServiceOperationError


@component(ServiceManager)
class UpstartServiceManager(ServiceManager):
    id = 'upstart'
    name = 'Upstart'

    @classmethod
    def __verify__(cls):
        try:
            UpstartSystem()
            return True
        except:
            try:
                UpstartSystem(bus=DirectUpstartBus())
                return True
            except:
                return False

    def __init__(self, context):
        self.bus = None
        try:
            self.upstart = UpstartSystem()
        except:
            self.bus = DirectUpstartBus()
            self.upstart = UpstartSystem(bus=self.bus)

    def __fix_name(self, name):
        return name.replace('_2d', '-').replace('_2e', '.')

    def list(self):
        for job_name in self.upstart.get_all_jobs():
            yield self.get_service(job_name)

    def get_service(self, _id):
        job = UpstartJob(_id, bus=self.bus)
        svc = Service(self)
        svc.id = _id
        svc.name = self.__fix_name(_id)
        try:
            svc.state = job.get_status()['state']
            svc.running = svc.state == 'running'
        except:
            svc.running = False
        return svc

    def start(self, _id):
        try:
            UpstartJob(_id).start()
        except DBusException as e:
            raise ServiceOperationError(e)

    def stop(self, _id):
        try:
            UpstartJob(_id).stop()
        except DBusException as e:
            raise ServiceOperationError(e)

    def restart(self, _id):
        try:
            UpstartJob(_id).restart()
        except DBusException as e:
            raise ServiceOperationError(e)
