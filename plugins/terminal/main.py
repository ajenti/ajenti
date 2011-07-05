from ajenti.api import *
from ajenti.utils import *
from ajenti.ui import *

import os
import threading
import shlex
import signal
import json
import gzip
import StringIO
from base64 import b64decode, b64encode

from twisted.internet import protocol
from twisted.internet import reactor

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
        self._proc = PTYProtocol()
        env = os.environ
        env['TERM'] = 'linux'
        env['COLUMNS'] = str(TERM_W)
        env['LINES'] = str(TERM_H)
        sh = self.app.get_config(self).shell
        reactor.spawnProcess(
            self._proc, 
            shlex.split(sh)[0], 
            shlex.split(sh), 
            usePTY=True, 
            env=env
        )
        
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
        
    
class PTYProtocol(protocol.ProcessProtocol):
    def __init__(self):
        self.data = ''
        self.lock = threading.Lock()
        self.cond = threading.Condition()
        self.term = pyte.DiffScreen(TERM_W,TERM_H)
        self.stream = pyte.Stream()
        self.stream.attach(self.term)
        
    def connectionMade(self):
        pass
            
    def outReceived(self, data):
        with self.cond:
            with self.lock:
                self.data += data
            self.cond.notifyAll()        

    def read(self):
        with self.cond:
            if len(self.data) == 0:
                self.cond.wait(15)
            with self.lock:
                data = self.data
                self.data = ''
                if len(data) > 0:
                    self.stream.feed(unicode(str(data)))
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
        self.transport.write(data)

    def kill(self):
        if self.transport.pid:
            os.kill(self.transport.pid, signal.SIGKILL)

