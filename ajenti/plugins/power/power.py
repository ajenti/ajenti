import logging
import subprocess
import os

from ajenti.api import plugin, interface
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget
from ajenti.ui import on
from ajenti.users import PermissionProvider, restrict


@plugin
class PowerSensor (Sensor):
    id = 'power'
    timeout = 2

    def measure(self, variant):
        adapters_path = '/proc/acpi/ac_adapter'
        if os.path.exists(adapters_path):
            for x in os.listdir(adapters_path):
                ss = open('/proc/acpi/ac_adapter/%s/state' % x).read().splitlines()
                for s in ss:
                    if s.startswith('state:') and s.endswith('on-line'):
                        return 'ac'
        else:
            return 'ac'
        return 'battery'

@interface
class PowerController (object):
    def shutdown(self):
        pass

    def suspend(self):
        pass

    def hibernate(self):
        pass

    def reboot(self):
        pass

    def capabilities(self):
        pass

@plugin
class SystemdPowerController (PowerController):
    def shutdown(self):
        subprocess.call(['systemctl', 'poweroff'])

    def reboot(self):
        subprocess.call(['systemctl', 'reboot'])

    def suspend(self):
        subprocess.call(['systemctl', 'suspend'])

    def hibernate(self):
        subprocess.call(['systemctl', 'hibernate'])

    def capabilities(self):
        try:
            subprocess.call(['which', 'systemctl'])
            return ['reboot', 'suspend', 'hibernate', 'shutdown']
        except:
            return []

    def verify(self):
        return bool(self.capabilities())

@plugin
class PMUtilsPowerController (PowerController):
    def shutdown(self):
        subprocess.call(['poweroff'])

    def suspend(self):
        subprocess.call(['pm-suspend'])

    def hibernate(self):
        subprocess.call(['pm-hibernate'])

    def reboot(self):
        subprocess.call(['reboot'])

    def capabilities(self):
        result = ['shutdown', 'reboot']
        try:
            subprocess.call(['which', 'pm-suspend'])
            result.append('suspend')
        except:
            pass

        try:
            subprocess.call(['which', 'pm-hibernate'])
            result.append('hibernate')
        except:
            pass

        return result

    def verify(self):
        return len(self.capabilities()) > 2

@plugin
class BatterySensor (Sensor):
    id = 'battery'
    timeout = 2

    def measure(self, variant):
        battery_path = '/proc/acpi/battery'

        if os.path.exists(battery_path):
            for x in os.listdir(battery_path):
                current = total = 100
                for s in open('/proc/acpi/battery/%s/state' % x).read().split('\n'):
                    if s.startswith('remaining capacity:'):
                        current = int(s.split()[2])

                for s in open('/proc/acpi/battery/%s/info' % x).read().split('\n'):
                    if s.startswith('last full capacity:'):
                        total = int(s.split()[3])

                return (current, total)

        return (1, 1)


@plugin
class PowerWidget (DashboardWidget):
    name = _('Power')
    icon = 'bolt'

    def init(self):
        self.sensor = Sensor.find('power')
        self.append(self.ui.inflate('power:widget'))
        self.find('ac').visible = self.sensor.value() == 'ac'
        self.find('battery').visible = self.sensor.value() == 'battery'
        charge = Sensor.find('battery').value()
        self.find('charge').value = charge[0] * 1.0 / charge[1]

        self.powerctl = PowerController.get()
        caps = self.powerctl.capabilities()
        for cap in ('shutdown', 'suspend', 'hibernate', 'reboot'):
            self.find(cap).visible = cap in caps

    @on('suspend', 'click')
    @restrict('power:suspend')
    def on_suspend(self):
        logging.info('[power] suspend')
        self.powerctl.suspend()

    @on('hibernate', 'click')
    @restrict('power:hibernate')
    def on_hibernate(self):
        logging.info('[power] hibernate')
        self.powerctl.hibernate()

    @on('reboot', 'click')
    @restrict('power:reboot')
    def on_reboot(self):
        logging.info('[power] reboot')
        self.powerctl.reboot()

    @on('shutdown', 'click')
    @restrict('power:shutdown')
    def on_shutdown(self):
        logging.info('[power] poweroff')
        self.powerctl.shutdown()


@plugin
class PowerPermissionsProvider (PermissionProvider):
    def get_name(self):
        return _('Power control')

    def get_permissions(self):
        return [
            ('power:suspend', _('Suspend')),
            ('power:hibernate', _('Hibernate')),
            ('power:reboot', _('Reboot')),
            ('power:shutdown', _('Shutdown')),
        ]
