from __future__ import unicode_literals
from ajenti.util import LazyModule

import locale
import logging
import os
psutil = LazyModule('psutil') # -2MB
import signal
import socket
import sys
import syslog
import traceback


import ajenti

import ajenti.plugins
from ajenti.http import HttpRoot, RootHttpHandler, HttpMiddlewareAggregator
from ajenti.gate.middleware import GateMiddleware
from ajenti.plugins import *
from ajenti.api import *
from ajenti.util import make_report

import gevent
import gevent.ssl
from gevent import monkey

# Gevent monkeypatch ---------------------
try:
    monkey.patch_all(select=True, thread=True, aggressive=False, subprocess=True)
except:
    monkey.patch_all(select=True, thread=True, aggressive=False)  # old gevent

from gevent.event import Event
import threading
threading.Event = Event
# ----------------------------------------

import ajenti.compat

from socketio.server import SocketIOServer
from socketio.handler import SocketIOHandler


def run():
    ajenti.init()

    reload(sys)
    sys.setdefaultencoding('utf8')

    try:
        locale.setlocale(locale.LC_ALL, '')
    except:
        logging.warning('Couldn\'t set default locale')

    logging.info('Ajenti %s running on platform: %s' % (ajenti.version, ajenti.platform))
    if not ajenti.platform in ['debian', 'centos', 'freebsd', 'mageia']:
        logging.warn('%s is not officially supported!' % ajenti.platform)

    # Load plugins
    ajenti.context = Context()
    PluginManager.get(ajenti.context).load_all()
    if len(PluginManager.get(ajenti.context).get_all()) == 0:
        logging.warn('No plugins were loaded!')

    if 'socket' in ajenti.config['bind']:
        addrs = socket.getaddrinfo(bind_spec[0], bind_spec[1], socket.AF_INET6, 0, socket.SOL_TCP)
        bind_spec = addrs[0][-1]
    else:
        bind_spec = (ajenti.config['bind']['host'], ajenti.config['bind']['port'])

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
        if not ajenti.platform in ['freebsd', 'osx']:
            try:
                listener.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
            except:
                logging.warn('Could not set TCP_CORK')
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listener.bind(bind_spec)
        except:
            logging.error('Could not bind to %s' % (bind_spec,))
            sys.exit(1)
        listener.listen(10)

    gateway = GateMiddleware.get(ajenti.context)
    application = HttpRoot(HttpMiddlewareAggregator([gateway])).dispatch

    ssl_args = {}
    if ajenti.config['ssl']['enable']:
        ssl_args['certfile'] = ajenti.config['ssl']['certificate_path']
        logging.info('SSL enabled: %s' % ssl_args['certfile'])


    def handle_one_response(self):
        path = self.environ.get('PATH_INFO')
        prefix = self.environ.get('HTTP_X_URL_PREFIX', '')
        self.server.resource = (prefix + '/socket.io').strip('/')
        response = handle_one_response.original(self)
        self.server.response = 'socket.io'
        return response
        
    handle_one_response.original = SocketIOHandler.handle_one_response
    SocketIOHandler.handle_one_response = handle_one_response

    ajenti.server = SocketIOServer(
        listener,
        log=open(os.devnull, 'w'),
        application=application,
        policy_server=False,
        handler_class=RootHttpHandler,
        resource='socket.io',
        transports=[
            str('websocket'),
            str('flashsocket'),
            str('xhr-polling'),
            str('jsonp-polling'),
        ],
        **ssl_args
    )

    # auth.log
    try:
        syslog.openlog(
            ident=str(b'ajenti'),
            facility=syslog.LOG_AUTH,
        )
    except:
        syslog.openlog(b'ajenti')


    def cleanup():
        if hasattr(cleanup, '_started'):
            return
        cleanup._started = True
        logging.info('Process %s exiting normally' % os.getpid())
        gevent.signal(signal.SIGINT, lambda: None)
        gevent.signal(signal.SIGTERM, lambda: None)
        if ajenti.master:
            gateway.destroy()

        p = psutil.Process(os.getpid())
        for c in p.get_children(recursive=True):
            try:
                os.killpg(c.pid, signal.SIGTERM)
                os.killpg(c.pid, signal.SIGKILL)
            except OSError:
                pass
        sys.exit(0)

    try:
        gevent.signal(signal.SIGINT, cleanup)
        gevent.signal(signal.SIGTERM, cleanup)
    except:
        pass

    ajenti.server.serve_forever()

    if not ajenti.master:
        while True:
            gevent.sleep(3600)

    if hasattr(ajenti.server, 'restart_marker'):
        logging.warn('Restarting by request')
        cleanup()

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
        if ajenti.master:
            logging.debug('Server stopped')



def handle_crash(exc):
    logging.error('Fatal crash occured')
    traceback.print_exc()
    exc.traceback = traceback.format_exc(exc)
    report_path = '/root/ajenti-crash.txt'
    try:
        report = open(report_path, 'w')
    except:
        report_path = './ajenti-crash.txt'
        report = open(report_path, 'w')
    report.write(make_report(exc))
    report.close()
    logging.error('Crash report written to %s' % report_path)
    logging.error('Please submit it to https://github.com/Eugeny/ajenti/issues/new')
