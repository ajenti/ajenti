from ajenti.com import *
from ajenti.api import *
from ajenti.utils import *
from ajenti.ui import UI
from ajenti import apis
import os
import time

class Daemons(Plugin):

    def list_all(self):
        r = []
        for n in self.app.config.options('daemons'):
            l = self.app.config.get('daemons', n)
            r.append(Daemon(n, l))
        return sorted(r, key=lambda x: x.name)

    def save(self, items):
        self.app.config.remove_section('daemons')
        self.app.config.add_section('daemons')

        for i in items:
            x = []
            for k in i.opts.keys():
                if k is None or k == '':
                    continue
                if i.opts[k] == None:
                    x.append(k)
                else:
                    x.append('%s="%s"'%(k,i.opts[k].strip(' "')))
            self.app.config.set('daemons', i.name, ','.join(x))

        self.app.config.save()


class Daemon:
    def __init__(self, name, s):
        self.name = name
        self.opts = {}
        for x in s.split(','):
            v = None
            if '=' in x:
                k,v = x.split('=',1)
                v = v.strip(' "')
            else:
                k = x
            self.opts[k.strip()] = v

    @property
    def running(self):
        u = ''
        if 'user' in self.opts:
            u = ' --user="%s"'%self.opts['user']
        return shell_status('daemon --running --name "%s"%s'%(self.name,u)) == 0

    def start(self):
        cmd = ''
        for k in self.opts.keys():
            if k is None or k == '':
                continue
            if self.opts[k] == None:
                cmd += ' --%s' % k
            else:
                cmd += ' --%s "%s"'%(k,self.opts[k])
        shell('daemon --name "%s" %s'%(self.name, cmd))
        time.sleep(0.5)

    def restart(self):
        u = ''
        if 'user' in self.opts:
            u = ' --user="%s"'%self.opts['user']
        shell('daemon --restart --name "%s"%s'%(self.name,u))
        self.running
        time.sleep(0.5)

    def stop(self):
        u = ''
        if 'user' in self.opts:
            u = ' --user="%s"'%self.opts['user']
        shell('daemon --stop --name "%s"%s'%(self.name,u))
        self.running
        time.sleep(0.5)

options = [
    'command',
    'user',
    'chroot',
    'chdir',
    'umask',
    'attempts',\
    'delay',
    'limit',
    'output',
    'stdout',
    'stderr',
]
