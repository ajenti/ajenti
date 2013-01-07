import logging
import signal
import syslog
import sys

import ajenti
from ajenti.http import HttpRoot
from ajenti.routing import CentralDispatcher
from ajenti.middleware import SessionMiddleware, AuthenticationMiddleware
import ajenti.plugins


import gevent
from gevent import monkey
monkey.patch_all()
from socketio.server import SocketIOServer


def run():
    logging.info('Ajenti %s running on platform: %s' % (ajenti.version, ajenti.platform))

    # Load plugins
    ajenti.plugins.manager.load_all()

    ssl = {}
    if ajenti.config.tree.ssl.enable:
        ssl = {
            'certfile':  ajenti.config.tree.ssl.certificate_path,
            'keyfile': ajenti.config.tree.ssl.key_path,
            'ciphers': 'RC4-SHA',
        }

    stack = [SessionMiddleware(), AuthenticationMiddleware(), CentralDispatcher()]
    ajenti.server = SocketIOServer(
        (ajenti.config.tree.http_binding.host,
         ajenti.config.tree.http_binding.port),
        application=HttpRoot(stack).dispatch,
        **ssl
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
