import dbus
import subprocess

from ajenti.api import *

from api import Service, ServiceManager


@plugin
class UpstartServiceManager (ServiceManager):
    def init(self):
        self.bus = dbus.SystemBus()
        self.upstart = self.bus.get_object("com.ubuntu.Upstart", "/com/ubuntu/Upstart")

    def get_all(self):
        jobs = self.upstart.GetAllJobs(dbus_interface="com.ubuntu.Upstart0_6")
        r = []
        for job in jobs:
            obj = self.bus.get_object("com.ubuntu.Upstart", job)
            jprops = obj.GetAll("com.ubuntu.Upstart0_6.Job", dbus_interface=dbus.PROPERTIES_IFACE)

            s = Service()
            s.name = str(jprops['name'])

            paths = obj.GetAllInstances(dbus_interface="com.ubuntu.Upstart0_6.Job")
            if len(paths) > 0:
                instance = self.bus.get_object("com.ubuntu.Upstart", paths[0])
                iprops = instance.GetAll("com.ubuntu.Upstart0_6.Instance", dbus_interface=dbus.PROPERTIES_IFACE)
                s.running = str(iprops['state']) == 'running'
            else:
                s.running = False

            r.append(s)
        return r

    def start(self, service):
        subprocess.call(['start', service.name])

    def stop(self, service):
        subprocess.call(['stop', service.name])

    def restart(self, service):
        subprocess.call(['restart', service.name])
