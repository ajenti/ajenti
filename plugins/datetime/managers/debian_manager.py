import os
import pytz
from jadi import component

import aj
from aj.plugins.datetime.api import TZManager


@component(TZManager)
class DebianTZManager(TZManager):
    @classmethod
    def __verify__(cls):
        return aj.platform in ['debian', 'gentoo']

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
