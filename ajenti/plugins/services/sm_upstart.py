try:
    import dbus
except ImportError:
    pass

import subprocess

from ajenti.api import *
from ajenti.util import cache_value

from api import Service, ServiceManager


@plugin
class UpstartServiceManager (ServiceManager):
    platforms = ['debian']

    def init(self):
        self.bus = dbus.SystemBus()
        self.upstart = self.bus.get_object("com.ubuntu.Upstart", "/com/ubuntu/Upstart")

    @classmethod
    def verify(cls):
        try:
            c = cls()
            c.init()
            return True
        except:
            return False

    @cache_value(1)
    def get_all(self):
        try:
            jobs = self.upstart.GetAllJobs(dbus_interface="com.ubuntu.Upstart0_6")
            r = []
            for job in jobs:
                obj = self.bus.get_object("com.ubuntu.Upstart", job)
                jprops = obj.GetAll("com.ubuntu.Upstart0_6.Job", dbus_interface=dbus.PROPERTIES_IFACE)

                s = UpstartService(str(jprops['name']))

                paths = obj.GetAllInstances(dbus_interface="com.ubuntu.Upstart0_6.Job")
                if len(paths) > 0:
                    instance = self.bus.get_object("com.ubuntu.Upstart", paths[0])
                    iprops = instance.GetAll("com.ubuntu.Upstart0_6.Instance", dbus_interface=dbus.PROPERTIES_IFACE)
                    s.running = str(iprops['state']) == 'running'
                else:
                    s.running = False

                r.append(s)
            return r
        except dbus.DBusException:
            return []


class UpstartService (Service):
    source = 'upstart'

    def __init__(self, name):
        self.name = name

    def refresh(self):
        self.running = 'running' in subprocess.check_output(['status', self.name])

    def start(self):
        subprocess.call(['start', self.name])

    def stop(self):
        subprocess.call(['stop', self.name])

    def restart(self):
        subprocess.call(['restart', self.name])

    def command(self, cmd):
        subprocess.call(['/etc/init.d/%s' % self.name, 'cmd'])
