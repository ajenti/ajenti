import os
import pytz

from aj.api import component
from aj.plugins.datetime.api import TZManager


@component(TZManager)
class DebianTZManager(TZManager):
    def __init__(self, context):
        TZManager.__init__(self, context)

    def get_tz(self):
        return open('/etc/timezone').read().strip()

    def set_tz(self, name):
        open('/etc/timezone', 'w').write(name + '\n')
        tz = os.path.join('/usr/share/zoneinfo/', name)
        if os.path.exists('/etc/localtime'):
            os.unlink('/etc/localtime')
        os.symlink(tz, '/etc/localtime')

    def list_tz(self):
        return list(pytz.all_timezones)
