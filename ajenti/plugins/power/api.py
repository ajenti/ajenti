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
    def capabilities(cls):
        if subprocess.call(['which', 'systemctl']) == 0:
            return ['reboot', 'suspend', 'hibernate', 'shutdown']
        else:
            return []

    @classmethod
    @cache_value()
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
    def capabilities(cls):
        result = ['shutdown', 'reboot']
        if subprocess.call(['which', 'pm-suspend']) == 0:
            result.append('suspend')
        if subprocess.call(['which', 'pm-hibernate']) == 0:
            result.append('hibernate')
        return result

    @classmethod
    @cache_value()
    def verify(cls):
        return len(cls.capabilities()) > 2
