import os
import pytz
from jadi import component

import aj
from aj.plugins.datetime.api import TZManager


@component(TZManager)
class CentOSTZManager(TZManager):
    @classmethod
    def __verify__(cls):
        return aj.platform in ['centos']

    def __init__(self, context):
        TZManager.__init__(self, context)

    def get_tz(self):
        return os.path.realpath('/etc/localtime')[len('/usr/share/zoneinfo/'):] if os.path.islink('/etc/localtime') else None

    def set_tz(self, name):
        if not name:
            return
        tz = os.path.join('/usr/share/zoneinfo/', name)
        if os.path.exists('/etc/localtime'):
            os.unlink('/etc/localtime')
        os.symlink(tz, '/etc/localtime')

    def list_tz(self):
        return list(pytz.all_timezones)
