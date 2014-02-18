import subprocess

from ajenti.api import *
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
        for line in subprocess.check_output(['chkconfig', '--list']).splitlines():
            tokens = line.split()
            if len(tokens) < 3:
                continue

            name = tokens[0]
            s = SysVInitService(name)
            pending[s] = s._begin_refresh()
            r.append(s)
      
        for s,v in pending.iteritems():
            s._end_refresh(v)
        return r
