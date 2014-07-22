import gevent
import logging
import os
import subprocess

from ajenti.api import *
from ajenti.api.helpers import subprocess_call_background, subprocess_check_output_background
from ajenti.util import cache_value

from api import Service, ServiceManager


@plugin
class SysVInitServiceManager (ServiceManager):
    platforms = ['debian']

    @cache_value(1)
    def get_all(self):
        r = []
        found_names = []

        for line in subprocess_check_output_background(['service', '--status-all']).splitlines():
            tokens = line.split()
            if len(tokens) < 3:
                continue

            name = tokens[3]
            status = tokens[1]
            if status == '?':
                continue

            if name in found_names:
                continue

            s = SysVInitService(name)
            s.running = status == '+'
            r.append(s)

        return r

    def get_one(self, name):
        s = SysVInitService(name)
        if os.path.exists(s.script):
            s.refresh()
            return s

        return None


class SysVInitService (Service):
    source = 'sysvinit'

    def __init__(self, name):
        self.name = name
        self.script = '/etc/init.d/%s' % self.name

    def refresh(self):
        self.running = subprocess.call([self.script, 'status']) == 0

    def start(self):
        self.command('start')

    def stop(self):
        self.command('stop')

    def restart(self):
        self.command('restart')

    def command(self, cmd):
        try:
            p = subprocess.Popen([self.script, cmd], close_fds=True)
            gevent.sleep(0)
            p.wait()
        except OSError as e:
            logging.warn('service script failed: %s - %s' % (self.script, e))
