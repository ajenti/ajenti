import atexit
import logging
import os
import signal
import socket
import subprocess
import syslog
import sys
import time

import ajenti
from ajenti.http import HttpRoot
from ajenti.routing import CentralDispatcher
from ajenti.middleware import SessionMiddleware, AuthenticationMiddleware
import ajenti.plugins

import gevent
from gevent import monkey
monkey.patch_all()
from socketio.server import SocketIOServer


class SSLTunnel (object):
    """
    gevent's SSL server implementation is buggy so we have to use stunnel
    """

    def start(self, host, port, certificate_path):
        self.port = self.get_free_port()
        logging.info('Starting SSL tunnel for port %i' % self.port)
        self.process = subprocess.Popen([
            'stunnel',
            '-p', certificate_path,
            '-r', '127.0.0.1:%i' % self.port,
            '-d', '%s:%i' % (host or '0.0.0.0', port),
            '-f',
            '-P', '',
            '-o', os.devnull,
            '-D', '0'])

    def check(self):
        time.sleep(0.5)
        return self.process.poll() is None

    def stop(self):
        self.process.terminate()

    def get_free_port(self):
        s = socket.socket()
        s.bind(('', 0))
        port = s.getsockname()[1]
        s.close()
        return int(port)


def run():
    logging.info('Ajenti %s running on platform: %s' % (ajenti.version, ajenti.platform))

    # Load plugins
    ajenti.plugins.manager.load_all()

    bind_spec = (ajenti.config.tree.http_binding.host, ajenti.config.tree.http_binding.port)

    if ajenti.config.tree.ssl.enable:
        ssl_tunnel = SSLTunnel()
        ssl_tunnel.start(bind_spec[0], bind_spec[1], ajenti.config.tree.ssl.certificate_path)
        if ssl_tunnel.check():
            logging.info('SSL tunnel running fine')
            bind_spec = ('127.0.0.1', ssl_tunnel.port)
            atexit.register(ssl_tunnel.stop)
        else:
            logging.error('SSL tunnel failed to start')

    stack = [SessionMiddleware(), AuthenticationMiddleware(), CentralDispatcher()]
    ajenti.server = SocketIOServer(
        bind_spec,
        log=open(os.devnull, 'w'),
        application=HttpRoot(stack).dispatch,
    )

    # auth.log
    try:
        syslog.openlog(
            ident='ajenti',
            facility=syslog.LOG_AUTH,
        )
    except:
        syslog.openlog('ajenti')

    try:
        gevent.signal(signal.SIGTERM, lambda: sys.exit(0))
    except:
        pass

    ajenti.server.serve_forever()
