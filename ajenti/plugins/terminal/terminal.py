import os
import sys
import subprocess as sp
import fcntl
import pty
import gevent

import pyte


class Terminal (object):
    def __init__(self, command=None):
        self.protocol = None
        self.width = 160
        self.height = 35

        env = {}
        env.update(os.environ)
        env['TERM'] = 'linux'
        env['COLUMNS'] = str(self.width)
        env['LINES'] = str(self.height)
        env['LC_ALL'] = 'en_US.UTF8'

        command = command or 'sh -c \"$SHELL\"',
        print 'launching',   command
        pid, master = pty.fork()
        if pid == 0:
            p = sp.Popen(
                command,
                shell=True,
                close_fds=True,
                env=env,
            )
            p.wait()
            sys.exit(0)
        self.screen = pyte.DiffScreen(self.width, self.height)
        self.protocol = PTYProtocol(pid, master, self.screen)

    def restart(self):
        if self.protocol is not None:
            self.protocol.kill()
        self.start()

    def dead(self):
        return self.protocol is None

    def write(self, data):
        self.protocol.write(data)

    def kill(self):
        self.protocol.kill()


class PTYProtocol():
    def __init__(self, pid, master, term):
        self.data = ''
        self.pid = pid
        self.master = master
        self.dead = False

        fd = self.master
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        self.mstream = os.fdopen(self.master, 'r+')
        gevent.sleep(0.5)
        self.term = term
        self.stream = pyte.Stream()
        self.stream.attach(self.term)
        self.data = ''
        self.unblock()

    def unblock(self):
        fd = self.master
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    def block(self):
        fd = self.master
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl - os.O_NONBLOCK)

    def read(self):
        for i in range(0, 45):
            try:
                d = self.mstream.read()
                #if not d:
                #    self.dead = True
                #    return self.format()
                self.data += d
                if len(self.data) > 0:
                    u = unicode(str(self.data))
                    self.stream.feed(u)
                    self.data = ''
                break
            except IOError:
                pass
            except UnicodeDecodeError:
                pass
            gevent.sleep(0.33)
        return self.format()

    def history(self):
        return self.format(full=True)

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
        self.block()
        self.mstream.write(data)
        self.mstream.flush()
        self.unblock()

    def kill(self):
        os.kill(self.pid, 9)
