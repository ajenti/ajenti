import subprocess
import os


# add subprocess.check_output to Python < 2.6
if not hasattr(subprocess, 'check_output'):
    def c_o(*args, **kwargs):
        kwargs['stdout'] = kwargs['stderr'] = subprocess.PIPE
        popen = subprocess.Popen(*args, **kwargs)
        popen.wait()
        return popen.stdout.read() + popen.stderr.read()
    subprocess.check_output = c_o


old_Popen = subprocess.Popen.__init__


def Popen(*args, **kwargs):
    __null = open(os.devnull, 'w')
    return old_Popen(
        stdin=kwargs.pop('stdin', subprocess.PIPE),
        stdout=kwargs.pop('stdout', __null),
        stderr=kwargs.pop('stderr', __null),
        *args, **kwargs)

subprocess.Popen.__init__ = Popen


# fix AttributeError
# a super-rude fix - DummyThread doesn't have a __block so provide an acquired one
import threading


def tbget(self):
    if hasattr(self, '__compat_lock'):
        return self.__compat_lock
    c = threading.Condition()
    c.acquire()
    return c


def tbset(self, l):
    self.__compat_lock = l


def tbdel(self):
    del self.__compat_lock

threading.Thread._Thread__block = property(tbget, tbset, tbdel)


# suppress Requests logging
import logging

logging.getLogger("requests").setLevel(logging.WARNING)
