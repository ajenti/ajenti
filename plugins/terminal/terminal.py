from gevent.socket import wait_read, wait_write
import fcntl
import gevent
import logging
import os
import pty
import setproctitle
import signal
import struct
import subprocess
import sys
import termios

import pyte

from aj.util import BroadcastQueue


class Terminal (object):
    def __init__(self, manager=None, id=None, command=None, autoclose=False):
        self.width = 80
        self.height = 25
        self.id = id
        self.manager = manager
        self.autoclose = autoclose
        self.output = BroadcastQueue()

        env = {}
        env.update(os.environ)
        env['TERM'] = 'linux'
        env['COLUMNS'] = str(self.width)
        env['LINES'] = str(self.height)
        env['LC_ALL'] = 'en_US.UTF8'

        if not command:
            shell = os.environ.get('SHELL', None)
            if not shell:
                for sh in ['zsh', 'bash', 'sh']:
                    try:
                        shell = subprocess.check_output(['which', sh])
                        break
                    except:
                        pass
            self.command = shell
            args = [shell]
            exe = shell
        else:
            self.command = command
            args = ['sh', '-c', self.command]
            exe = 'sh'

        logging.info('Activating new terminal: %s' % self.command)

        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            setproctitle.setproctitle('%s terminal session #%i' % (sys.argv[0], os.getpid()))
            os.execvpe(exe, args, env)

        logging.info('Subprocess PID %s' % self.pid)

        self.dead = False

        fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        self.stream = os.fdopen(self.fd, 'r+')
        self.pyte_stream = pyte.Stream()
        self.screen = pyte.DiffScreen(self.width, self.height)
        self.pyte_stream.attach(self.screen)

        self.last_cursor_position = None

        self.reader = gevent.spawn(self.reader)

    def reader(self):
        data = ''
        while True:
            wait_read(self.fd)

            try:
                d = self.stream.read()
            except IOError:
                d = ''

            try:
                data += d
                self._check()
                if self.dead:
                    return
                if data:
                    u = data.decode('utf-8')
                    self.pyte_stream.feed(u)
                    data = ''
                    self.broadcast_update()
                    continue
            except UnicodeDecodeError:
                continue

    def broadcast_update(self):
        self.output.broadcast(self.format())

    def _check(self):
        try:
            pid, status = os.waitpid(self.pid, os.WNOHANG)
        except OSError:
            self.on_died(code=0)
            return
        if pid:
            self.on_died(code=status)

    def on_died(self, code=0):
        if self.dead:
            return

        self.dead = True

        if code:
            self.pyte_stream.feed(u'\n\n * ' + u'Process has exited with status %i' % code)
        else:
            self.pyte_stream.feed(u'\n\n * ' + u'Process has exited successfully')

        self.broadcast_update()
        if self.autoclose:
            self.manager.remove(self.id)
        """
        TODO
        if self.callback:
            try:
                self.callback(exitcode=code)
            except TypeError:
                self.callback()
        """

    def has_updates(self):
        if self.last_cursor_position != (self.screen.cursor.x, self.screen.cursor.y):
            return True
        return len(self.screen.dirty) > 0

    def format(self, full=False):
        def compress(line):
            return [[tok or 0 for tok in ch] for ch in line]

        l = {}
        self.screen.dirty.add(self.screen.cursor.y)
        if self.last_cursor_position:
            self.screen.dirty.add(self.last_cursor_position[1])
        for k in self.screen.dirty:
            if k < len(self.screen.buffer):
                l[k] = compress(self.screen.buffer[k])
        self.screen.dirty.clear()

        if full:
            l = [compress(x) for x in self.screen.buffer]

        r = {
            'lines': l,
            'cx': self.screen.cursor.x,
            'cy': self.screen.cursor.y,
            'cursor': not self.screen.cursor.hidden,
            'h': self.screen.size[0],
            'w': self.screen.size[1],
        }

        self.last_cursor_position = (self.screen.cursor.x, self.screen.cursor.y)
        return r

    def feed(self, data):
        wait_write(self.fd)
        self.stream.write(data)
        self.stream.flush()

    def resize(self, w, h):
        if (h, w) == self.screen.size:
            return
        if w <= 0 or h <= 0:
            return
        self.width = w
        self.height = h
        logging.debug('Resizing terminal to %sx%s' % (w, h))
        self.screen.resize(h, w)
        winsize = struct.pack("HHHH", h, w, 0, 0)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)

    def kill(self):
        self.reader.kill(block=False)

        logging.info('Killing subprocess PID %s' % self.pid)
        try:
            os.killpg(self.pid, signal.SIGTERM)
        except OSError:
            pass
        try:
            os.kill(self.pid, signal.SIGKILL)
        except OSError:
            pass
