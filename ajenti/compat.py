import logging
import subprocess
import os


# add subprocess.check_output to Python < 2.6
if not hasattr(subprocess, 'check_output'):
    def c_o(*args, **kwargs):
        kwargs['stdout'] = subprocess.PIPE
        popen = subprocess.Popen(*args, **kwargs)
        stdout, stderr = popen.communicate()
        return stdout
    subprocess.check_output = c_o


old_Popen = subprocess.Popen.__init__


def Popen(*args, **kwargs):
    logging.debug('Popen: %s' % (args[1],))
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


# fix AttributeError("'Event' object has no attribute '_reset_internal_locks'",)
import threading
if not hasattr(threading.Event, '_reset_internal_locks'):
    def r_i_l(self):
        pass
    threading.Event._reset_internal_locks = r_i_l


# suppress Requests logging
logging.getLogger("requests").setLevel(logging.WARNING)

# suppress simplejson
try:
    import simplejson
    _loads = simplejson.loads

    def wrap(fx):
        def f(*args, **kwargs):
            kwargs.pop('use_decimal', None)
            return fx(*args, **kwargs)
        return f

    simplejson.dumps = wrap(simplejson.dumps)
    simplejson.loads = wrap(simplejson.loads)
except:
    pass


# Suppress CORS headers in Socket.IO
from socketio.transports import BaseTransport

old_transport_init = BaseTransport.__init__

def new_transport_init(self, *args, **kwargs):
    old_transport_init(self, *args, **kwargs)
    self.headers = []

BaseTransport.__init__ = new_transport_init

