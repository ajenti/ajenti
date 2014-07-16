import os
import subprocess

from ajenti.api import *
from ajenti.api.helpers import subprocess_call_background, subprocess_check_output_background
from ajenti.util import cache_value

from api import ServiceManager
from sm_sysvinit import SysVInitService


@plugin
class CentOSServiceManager (ServiceManager):
    platforms = ['centos']

    @cache_value(1)
    def get_all(self):
        r = []
        pending = {}
        for line in subprocess_check_output_background(['chkconfig', '--list']).splitlines():
            tokens = line.split()
            if len(tokens) < 3:
                continue

            name = tokens[0]
            s = SysVInitService(name)
            s.refresh()
            r.append(s)

        return r

    def get_one(self, name):
        s = SysVInitService(name)
        if os.path.exists(s.script):
            s.refresh()
            return s
        return None
