from upstart.system import UpstartSystem, DirectUpstartBus
from upstart.job import UpstartJob

from aj.api import *
from aj.plugins.services.api import ServiceManager, Service


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
            yield self.get(job_name)

    def get(self, _id):
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
        UpstartJob(_id).start()

    def stop(self, _id):
        UpstartJob(_id).stop()

    def restart(self, _id):
        UpstartJob(_id).restart()
