import subprocess
import logging

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget
from ajenti.util import platform_select
from ajenti.ui import on
from ajenti.users import PermissionProvider, restrict

from ajenti.plugins.power.api import PowerController

@plugin
class RebootRequired (Sensor):
    id = 'needrestart'
    timeout = 1

    def measure(self, variant):
        output = subprocess.check_output(['needrestart', '-b']).strip()
        return output


@plugin
class RebootWidget (DashboardWidget):
    name = _('Need Restart')
    icon = 'restart'

    def init(self):
        self.sensor = Sensor.find('needrestart')
        self.append(self.ui.inflate('needrestart:widget'))

        self.find('icon').text = 'restart'
        self.find('name').text = _('Need Restart')
        restartRequired = True
        if "NEEDRESTART-KSTA: 3" in self.sensor.value():
            self.find('value').text = _('Reboot required')
            self.find('reboottooltip').visible = True
        elif "NEEDRESTART-KSTA: 1" in self.sensor.value() or "NEEDRESTART-KSTA: 2" in self.sensor.value():
            if "NEEDRESTART-SVC:" in self.sensor.value():
                self.find('value').text = _('Service restart required')
                self.find('needrestarttooltip').visible = True
            elif "NEEDRESTART-CONT:" in self.sensor.value():
                self.find('value').text = _('Container restart required')
                self.find('needrestarttooltip').visible = True
            else:
                self.find('value').text = _('no pending restart')
                restartRequired = False
        else:
            self.find('value').text = 'unknown state, output:\n' + self.sensor.value()

        if restartRequired:
            self.find('icon').style = 'yellow'
            self.find('icon').icon = 'warning-sign'
        self.powerctl = PowerController.get()

    @on('reboot', 'click')
    @restrict('needrestart:reboot')
    def on_reboot(self):
        logging.info('[needrestart] reboot')
        self.powerctl.reboot()

    @on('restart', 'click')
    @restrict('needrestart:restart')
    def on_restart(self):
        logging.info('[needrestart] restart services/containers')
        output = subprocess.check_output(['needrestart', '-r', 'a']).strip()        
        logging.info('[needrestart] '+output)
