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
        try:
            subprocess.call(['which', 'systemctl'])
            return ['reboot', 'suspend', 'hibernate', 'shutdown']
        except:
            return []

    @classmethod
    @cache_value()
    def verify(cls):
        return bool(cls.capabilities())


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

    @classmethod
    @cache_value()
    def verify(cls):
        return len(cls.capabilities()) > 2
