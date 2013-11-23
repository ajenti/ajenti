from __future__ import unicode_literals

import atexit
import exconsole
import locale
import logging
import os
import signal
import socket
import subprocess
import syslog
import sys
import time
import tempfile


import ajenti
import ajenti.locales  # importing locale before everything else!

import ajenti.feedback
import ajenti.ipc
import ajenti.plugins
from ajenti.http import HttpRoot
from ajenti.middleware import SessionMiddleware, AuthenticationMiddleware
from ajenti.plugins import manager
from ajenti.routing import CentralDispatcher
from ajenti.ui import Inflater

import gevent
from gevent import monkey
monkey.patch_all(select=False, thread=False)
from socketio.server import SocketIOServer


class SSLTunnel (object):
    """
    gevent's SSL server implementation is buggy so we have to use stunnel
    """

    def start(self, host, port, certificate_path):
        self.port = self.get_free_port()
        logging.info('Starting SSL tunnel for port %i' % self.port)
        stunnel = 'stunnel'
        if subprocess.call(['which', 'stunnel4']) == 0:
            stunnel = 'stunnel4'
        cfg = tempfile.NamedTemporaryFile(delete=False)
        cfg.write("""
            cert = %s
            foreground = yes
            pid =

            [default]
            accept = %s:%i
            connect = 127.0.0.1:%i
        """ % (
            certificate_path,
            host or '0.0.0.0', port,
            self.port
        ))
        cfg.close()
        cmd = [
            stunnel,
            cfg.name,
        ]
        self.process = subprocess.Popen(cmd, stdout=None)
        self._filename = cfg.name

    def check(self):
        time.sleep(0.5)
        return self.process.poll() is None

    def stop(self):
        os.unlink(self._filename)
        self.process.terminate()
        if self.check():
            self.process.kill()

    def get_free_port(self):
        s = socket.socket()
        s.bind(('', 0))
        port = s.getsockname()[1]
        s.close()
        return int(port)


def run():
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    try:
        locale.setlocale(locale.LC_ALL, '')
    except:
        logging.warning('Couldn\'t set default locale')

    logging.info('Ajenti %s running on platform: %s' % (ajenti.version, ajenti.platform))

    if ajenti.debug:
        exconsole.register()

    # Load plugins
    ajenti.plugins.manager.load_all()

    bind_spec = (ajenti.config.tree.http_binding.host, ajenti.config.tree.http_binding.port)
    if ':' in bind_spec[0]:
        addrs = socket.getaddrinfo(bind_spec[0], bind_spec[1], socket.AF_INET6, 0, socket.SOL_TCP)
        bind_spec = addrs[0][-1]

    ssl_tunnel = None
    if not bind_spec[0].startswith('/'):
        if ajenti.config.tree.ssl.enable:
            ssl_tunnel = SSLTunnel()
            ssl_tunnel.start(bind_spec[0], bind_spec[1], ajenti.config.tree.ssl.certificate_path)
            if ssl_tunnel.check():
                logging.info('SSL tunnel running fine')
                bind_spec = ('127.0.0.1', ssl_tunnel.port)
                atexit.register(ssl_tunnel.stop)
            else:
                logging.error('SSL tunnel failed to start')

    # Fix stupid socketio bug (it tries to do *args[0][0])
    socket.socket.__getitem__ = lambda x, y: None

    logging.info('Starting server on %s' % (bind_spec, ))
    if bind_spec[0].startswith('/'):
        if os.path.exists(bind_spec[0]):
            os.unlink(bind_spec[0])
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            listener.bind(bind_spec[0])
        except:
            logging.error('Could not bind to %s' % bind_spec[0])
            sys.exit(1)
        listener.listen(10)
    else:
        listener = socket.socket(socket.AF_INET6 if ':' in bind_spec[0] else socket.AF_INET, socket.SOCK_STREAM)
        try:
            listener.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
        except:
            try:
                socket.TCP_NOPUSH = 4
                listener.setsockopt(socket.IPPROTO_TCP, socket.TCP_NOPUSH, 1)
            except:
                logging.warn('Could not set TCP_CORK/TCP_NOPUSH')
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listener.bind(bind_spec)
        except:
            logging.error('Could not bind to %s' % (bind_spec,))
            sys.exit(1)
        listener.listen(10)

    stack = [SessionMiddleware(), AuthenticationMiddleware(), CentralDispatcher()]
    ajenti.server = SocketIOServer(
        listener,
        log=open(os.devnull, 'w'),
        application=HttpRoot(stack).dispatch,
        policy_server=False,
        resource='ajenti:socket',
    )

    # auth.log
    try:
        syslog.openlog(
            ident=str(b'ajenti'),
            facility=syslog.LOG_AUTH,
        )
    except:
        syslog.openlog(b'ajenti')

    try:
        gevent.signal(signal.SIGTERM, lambda: sys.exit(0))
    except:
        pass

    ajenti.feedback.start()
    ajenti.ipc.IPCServer.get(manager.context).start()

    Inflater.get(manager.context).precache()
    ajenti.server.serve_forever()

    if hasattr(ajenti.server, 'restart_marker'):
        logging.warn('Restarting by request')
        if ssl_tunnel:
            ssl_tunnel.stop()

        fd = 20  # Close all descriptors. Creepy thing
        while fd > 2:
            try:
                os.close(fd)
                logging.debug('Closed descriptor #%i' % fd)
            except:
                pass
            fd -= 1

        os.execv(sys.argv[0], sys.argv)
    else:
        logging.info('Stopped by request')
