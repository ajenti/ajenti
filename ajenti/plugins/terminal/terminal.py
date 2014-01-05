import os
import fcntl
import pty
import gevent
from gevent.select import select

import pyte


class Terminal (object):
    def __init__(self, command=None, autoclose=False, **kwargs):
        self.protocol = None
        self.width = 160
        self.height = 35
        self.autoclose = autoclose

        env = {}
        env.update(os.environ)
        env['TERM'] = 'linux'
        env['COLUMNS'] = str(self.width)
        env['LINES'] = str(self.height)
        env['LC_ALL'] = 'en_US.UTF8'

        command = ['sh', '-c', command or 'sh']

        pid, master = pty.fork()
        if pid == 0:
            os.execvpe('sh', command, env)

        self.screen = pyte.DiffScreen(self.width, self.height)
        self.protocol = PTYProtocol(pid, master, self.screen, **kwargs)

    def restart(self):
        if self.protocol is not None:
            self.protocol.kill()
        self.start()

    def dead(self):
        return self.protocol is None or self.protocol.dead

    def write(self, data):
        self.protocol.write(data)

    def kill(self):
        self.protocol.kill()


class PTYProtocol():
    def __init__(self, pid, master, term, callback=None):
        self.pid = pid
        self.master = master
        self.dead = False
        self.callback = callback

        fd = self.master
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        self.mstream = os.fdopen(self.master, 'r+')
        gevent.sleep(0.5)
        self.term = term
        self.stream = pyte.Stream()
        self.stream.attach(self.term)
        self.data = ''

    def read(self, timeout=1):
        select([self.master], [], [], timeout=timeout)
        
        try:
            d = self.mstream.read()
        except IOError:
            d = ''

        try:
            self.data += d
            if len(self.data) > 0:
                u = unicode(str(self.data))
                self.stream.feed(u)
                self.data = ''
                return None
        except UnicodeDecodeError:
            return None

        self._check()

    def _check(self):
        try:
            pid, status = os.waitpid(self.pid, os.WNOHANG)
        except OSError:
            self.on_died(code=-1)
            return
        if pid:
            self.on_died(code=status)

    def on_died(self, code=0):
        if self.dead:
            return
        self.dead = True
        if code:
            self.stream.feed('\n\n * ' + unicode(_('Process has exited with status %i') % code))
        else:
            self.stream.feed('\n\n * ' + unicode(_('Process has exited successfully')))
        if self.callback:
            try:
                self.callback(exitcode=code)
            except TypeError:
                self.callback()

    def history(self):
        return self.format(full=True)

    def has_updates(self):
        return len(self.term.dirty) > 0

    def format(self, full=False):
        l = {}
        self.term.dirty.add(self.term.cursor.y)
        for k in self.term.dirty:
            l[k] = self.term[k]
        self.term.dirty.clear()
        r = {
            'lines': self.term if full else l,
            'cx': self.term.cursor.x,
            'cy': self.term.cursor.y,
            'cursor': not self.term.cursor.hidden,
        }
        return r

    def write(self, data):
        self.mstream.write(data)
        self.mstream.flush()

    def kill(self):
        os.kill(self.pid, 9)
