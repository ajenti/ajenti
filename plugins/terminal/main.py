from ajenti.api import *
from ajenti.utils import *
from ajenti.ui import *

import os
import threading
import shlex
import signal
from base64 import b64decode, b64encode

from twisted.internet import protocol
from twisted.internet import reactor


class TerminalPlugin(CategoryPlugin, URLHandler):
    text = 'Terminal'
    icon = '/dl/terminal/icon.png'
    folder = 'tools'

    def on_session_start(self):
        self._proc = None
        
    def on_init(self):
        if self._proc is None:
            self.start();
    
    def get_ui(self):
        ui = self.app.inflate('terminal:main')
        return ui

    def start(self):
        self._proc = PTYProtocol()
        env = os.environ
        env['TERM'] = 'vt100'
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
        return b64encode(data)

    @url('^/term-post/.+')
    def post(self, req, start_response):
        data = req['PATH_INFO'].split('/')[2]
        self._proc.write(b64decode(data))
        return ''
    
    @event('button/click')
    def click(self, evt, params, vars):
        self.restart()
        
    
class PTYProtocol(protocol.ProcessProtocol):
    def __init__(self):
        self.data = ''
        self.hist = ''
        self.lock = threading.Lock()
        self.cond = threading.Condition()
        
    def connectionMade(self):
        pass
            
    def outReceived(self, data):
        with self.cond:
            with self.lock:
                self.data += data
                self.hist += data
                self.hist = self.hist[-2000:]
            self.cond.notifyAll()        

    def read(self):
        with self.cond:
            if len(self.data) == 0:
                self.cond.wait(5)
            with self.lock:
                data = self.data
                self.data = ''
        return data
        
    def history(self):
        return self.hist
        
    def write(self, data):
        self.transport.write(data)

    def kill(self):
        os.kill(self.transport.pid, signal.SIGKILL)

