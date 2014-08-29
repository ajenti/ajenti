import dbus
import logging
import subprocess

from ajenti.api import *
from ajenti.util import cache_value

from api import Service, ServiceManager



class UpstartService (Service):
    source = 'upstart'

    def __init__(self, name):
        self.name = name

    def refresh(self):
        self.running = 'running' in subprocess.check_output(['status', self.name])

    def start(self):
        self.command('start')

    def stop(self):
        self.command('stop')

    def restart(self):
        self.command('restart')

    def command(self, cmd):
        subprocess.Popen(['initctl', cmd, self.name], close_fds=True).wait()



@plugin
class UpstartServiceManager (ServiceManager):
    def init(self):
        self.bus = dbus.SystemBus()
        self.upstart = self.bus.get_object("com.ubuntu.Upstart", "/com/ubuntu/Upstart")

    @classmethod
    def verify(cls):
        try:
            c = cls()
            c.init()
            c.get_all()
            return True
        except Exception, e:
            logging.info('Disabling Upstart service manager: %s' % str(e))
            return False

    @cache_value(1)
    def get_all(self):
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
