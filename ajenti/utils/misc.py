import subprocess
import threading
import os
import sys
import trace

from utils import shell


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
            try:
                self.process.terminate()
            except:
                pass
            try:
                self.process.kill()
            except:
                pass


class BackgroundWorker:
    def __init__(self, *args):
        self.thread = KThread(target=self.__run, args=args)
        self.thread.daemon = True
        self.alive = False
        self.output = ''
        self._aborted = False
        
    def is_running(self):
        if self.alive:
            return not self.thread.killed
        return False
        
    def start(self):
        if not self.is_running():
            self.thread.start()
        self.alive = True
        
    def __run(self, *args):
        self.run(*args)
        self.alive = False
        
    def kill(self):
        self._aborted = True
        if self.is_running():
            self.thread.kill()
            
            
class KThread(threading.Thread):
    # A killable Thread class
    
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True            

