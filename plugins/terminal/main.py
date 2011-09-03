from ajenti.api import *
from ajenti.utils import *
from ajenti.ui import *

import os
import sys
import signal
import json
import gzip
import StringIO
import pty
import subprocess as sp
import fcntl
import pty
from base64 import b64decode, b64encode

from gevent.event import Event
import gevent

import pyte


TERM_W = 120
TERM_H = 30


class TerminalPlugin(CategoryPlugin, URLHandler):
    text = 'Terminal'
    icon = '/dl/terminal/icon.png'
    folder = 'tools'

    def on_session_start(self):
        self._proc = None
        self._inputting = False

    def on_init(self):
        if self._proc is None:
            self.start();

    def get_ui(self):
        ui = self.app.inflate('terminal:main')
        if self._inputting:
            ui.append('main', UI.CodeInputBox(
                id='dlgBatch',
                value='',
                text='Batch input:',
            ))
        return ui

    def start(self):
        env = {}
        env['TERM'] = 'linux'
        env['COLUMNS'] = str(TERM_W)
        env['LINES'] = str(TERM_H)
        env['LC_ALL'] = 'en_US.UTF8'
        sh = self.app.get_config(self).shell

        master, slave = pty.openpty()
        p = sp.Popen(
            sh,
            stdin=slave,
            stdiout=slave,
            stderr=slave,
            shell=True,
            close_fds=True,
            universal_newlines=True,
            env=env,
        )
        self._proc = PTYProtocol(p, master)

    def restart(self):
        if self._proc is not None:
            self._proc.kill()
        self.start()

    @url('^/term-get.*$')
    def get(self, req, start_response):
        if self._proc is None:
            self.start();
        if req['PATH_INFO'] == '/term-get-history':
            data = self._proc.history()
        else:
            data = self._proc.read()
        sio = StringIO.StringIO()
        gz = gzip.GzipFile(fileobj=sio, mode='w')
        gz.write(json.dumps(data))
        gz.close()
        return b64encode(sio.getvalue())

    @url('^/term-post/.+')
    def post(self, req, start_response):
        data = req['PATH_INFO'].split('/')[2]
        self._proc.write(b64decode(data))
        return ''

    @event('button/click')
    def click(self, evt, params, vars):
        if params[0] == 'restart':
            self.restart()
        if params[0] == 'input':
            self._inputting = True

    @event('dialog/submit')
    def submit(self, evt, params, vars=None):
        if vars.getvalue('action', None) == 'OK':
            self._proc.write(vars.getvalue('value', ''))
        self._inputting = False


class PTYProtocol():
    def __init__(self, proc, stream):
        self.data = ''
        self.proc = proc
        self.master = stream

        fd = self.master
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        self.mstream = os.fdopen(self.master, 'r+')
        gevent.sleep(2)
        self.term = pyte.DiffScreen(TERM_W,TERM_H)
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
        cond = Event()
        def reread():
            cond.set()
            cond.clear()
        for i in range(0,45):
            try:
                d = self.mstream.read()
                self.data += d
                if len(self.data) > 0:
                    print repr(self.data)
                    #u = unicode(self.data.encode('utf-8', 'xmlcharref'), errors='replace')
                    u = unicode(str(self.data))
                    self.stream.feed(u)
                    self.data = ''
                break
            except IOError, e:
                pass
            except UnicodeDecodeError, e:
                print 'UNICODE'
            gevent.spawn_later(0.33, reread)
            cond.wait(timeout=0.33)
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
        self.proc.kill()
