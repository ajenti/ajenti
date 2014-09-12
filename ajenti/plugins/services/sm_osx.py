import os
import subprocess

from ajenti.api import *
from ajenti.util import cache_value

from api import Service, ServiceManager


@plugin
class OSXServiceManager (ServiceManager):
    platforms = ['osx']

    @cache_value(1)
    def get_all(self):
        r = []
        for line in subprocess.check_output(['launchctl', 'list']).splitlines()[1:]:
            tokens = line.split()
            if len(tokens) == 3:
                s = OSXService(tokens[2])
                if s.name.startswith('com.apple'):
                    continue
                if not '.anonymous.' in s.name:
                    s.running = tokens[0] != '-'
                    r.append(s)
        return r


class OSXService (Service):
    source = 'launchd'

    def __init__(self, name):
        self.name = name

    def refresh(self):
        self.running = OSXServiceManager().get_one(self.name).running

    def start(self):
        self.command('start')

    def stop(self):
        self.command('stop')

    def restart(self):
        self.command('stop')
        self.command('start')

    def command(self, cmd):
        subprocess.call(['launchctl', cmd, self.name])
