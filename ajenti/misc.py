import subprocess
import threading
import os

class BackgroundProcess:
    thread = None
    process = None
    cmdline = None
    output = None
    errors = None
    exitcode = None
    alive = False
    _aborted = False
    
    def __init__(self, cmdline):
        self.thread = threading.Thread(target=self._run, args=[cmdline])
        self.output = ''
        self.errors = ''
        self.exitcode = None
        self.cmdline = cmdline
        self.alive = False
        self._aborted = False
        
    def is_running(self):
        return self.alive
        
    def start(self):
        if not self.is_running():
            self.thread.start()
        self.alive = True
        
    def _run(self, c):
        self.process = subprocess.Popen(c, shell=True,
                                           stderr=subprocess.PIPE,
                                           stdout=subprocess.PIPE,
                                           stdin=subprocess.PIPE)
        
        self.output += self.process.stdout.readline() # Workaround; waiting first causes a deadlock
        while self.process.returncode is None and not self._aborted:
            self.output += self.process.stdout.readline()
            self.process.poll()
        self.errors += self.process.stderr.read()
        self.exitcode = self.process.returncode
        self.alive = False
        
    def feed_input(self, data):
        if self.is_running():
            self.process.stdin.write(data)
    
    def kill(self):
        self._aborted = True
        if self.is_running():
            self.process.terminate()
            self.process.kill()

