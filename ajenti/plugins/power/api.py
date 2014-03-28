import subprocess

from ajenti.api import plugin, interface
from ajenti.util import cache_value


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

    @classmethod
    def capabilities(cls):
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

    @classmethod
    @cache_value()
    def capabilities(cls):
        if subprocess.call(['which', 'systemctl']) == 0:
            return ['reboot', 'suspend', 'hibernate', 'shutdown']
        else:
            return []

    @classmethod
    def verify(cls):
        return subprocess.call(['which', 'systemctl']) == 0


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

    @classmethod
    @cache_value()
    def capabilities(cls):
        return ['shutdown', 'reboot', 'suspend', 'hibernate']

    @classmethod
    def verify(cls):
        return subprocess.call(['which', 'pm-hibernate']) == 0


@plugin
class BasicLinuxPowerController (PowerController):
    def shutdown(self):
        subprocess.call(['poweroff'])

    def reboot(self):
        subprocess.call(['reboot'])

    @classmethod
    def capabilities(cls):
        return ['shutdown', 'reboot']
