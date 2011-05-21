from ajenti.api import *
from ajenti.utils import *
from ajenti.ui import *

import sys
import subprocess
import pty
import os
import threading
from base64 import b64decode, b64encode

from twisted.internet import protocol
from twisted.internet import reactor
import re


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
        reactor.spawnProcess(self._proc, '/bin/sh', ['/bin/sh'], usePTY=True, env={'TERM':'vt100'})
        
    @url('^/term-get$')
    def get(self, req, start_response):
        if self._proc is None:
            self.start();
        return b64encode(self._proc.read())

    @url('^/term-post/.+')
    def post(self, req, start_response):
        data = req['PATH_INFO'].split('/')[2]
        print data
        self._proc.write(b64decode(data))
        return ''#get(self, req, start_response)
    
    
    


class PTYProtocol(protocol.ProcessProtocol):
    def __init__(self):
        self.data = ''
        self.lock = threading.Lock()
        self.condition = threading.Condition()
        
    def connectionMade(self):
        pass
            
    def outReceived(self, data):
        print data
        with self.lock:
            self.data = self.data + data
            with self.condition:
                self.condition.notifyAll()
        
    def errReceived(self, data):
        print "errReceived! with %d bytes!" % len(data)
        
    def inConnectionLost(self):
        print "inConnectionLost! stdin is closed! (we probably did it)"
        
    def outConnectionLost(self):
        print "outConnectionLost! The child closed their stdout!"
        
    def errConnectionLost(self):
        print "errConnectionLost! The child closed their stderr."

    def processEnded(self, status_object):
        print "processEnded, status %d" % status_object.value.exitCode
        print "quitting"

    def read(self):
        """with self.condition:
            l = 0
            while l == 0:
                with self.lock:
                    l = len(self.data)
                if l == 0:
                    self.condition.wait()
        """
        with self.lock:
            data = self.data
            self.data = ''
        return data
        
    def write(self, data):
        self.transport.write(data)
                
