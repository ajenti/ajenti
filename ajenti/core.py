from __future__ import unicode_literals

import exconsole
import locale
import logging
import os
import signal
import socket
import sys
import syslog
import traceback


import ajenti
import ajenti.locales  # importing locale before everything else!

import ajenti.feedback
import ajenti.licensing
import ajenti.plugins
from ajenti.http import HttpRoot, RootHttpHandler
from ajenti.middleware import SessionMiddleware, AuthenticationMiddleware
from ajenti.plugins import manager
from ajenti.routing import CentralDispatcher
from ajenti.ui import Inflater
from ajenti.util import make_report

import gevent
import gevent.ssl
from gevent import monkey

import ajenti.ipc

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

    if ajenti.debug:
        def cmd_list_instances(ctx=None):
            import pprint
            if not ctx:
                from ajenti.plugins import manager
                ctx = manager.context
            pprint.pprint(ctx._get_all_instances())

        def cmd_sessions():
            import pprint
            sessions = SessionMiddleware.get().sessions
            return sessions

        def cmd_list_instances_session():
            cmd_list_instances(cmd_sessions().values()[0].appcontext)

        exconsole.register(commands=[
            ('_manager', 'PluginManager', ajenti.plugins.manager),
            ('_instances', 'return all @plugin instances', cmd_list_instances),
            ('_sessions', 'return all Sessions', cmd_sessions),
            ('_instances_session', 'return all @plugin instances in session #0', cmd_list_instances_session),
        ])

    # Load plugins
    ajenti.plugins.manager.load_all()
    Inflater.get().precache()

    bind_spec = (ajenti.config.tree.http_binding.host, ajenti.config.tree.http_binding.port)
    if ':' in bind_spec[0]:
        addrs = socket.getaddrinfo(bind_spec[0], bind_spec[1], socket.AF_INET6, 0, socket.SOL_TCP)
        bind_spec = addrs[0][-1]

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

    stack = [
        SessionMiddleware.get(),
        AuthenticationMiddleware.get(),
        CentralDispatcher.get()
    ]

    ssl_args = {}
    if ajenti.config.tree.ssl.enable:
        ssl_args['certfile'] = ajenti.config.tree.ssl.certificate_path
        ssl_args['ssl_version'] = gevent.ssl.PROTOCOL_TLSv1
        logging.info('SSL enabled: %s' % ssl_args['certfile'])

    ajenti.server = SocketIOServer(
        listener,
        log=open(os.devnull, 'w'),
        application=HttpRoot(stack).dispatch,
        policy_server=False,
        handler_class=RootHttpHandler,
        resource='ajenti:socket',
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

    try:
        gevent.signal(signal.SIGINT, lambda: sys.exit(0))
        gevent.signal(signal.SIGTERM, lambda: sys.exit(0))
    except:
        pass

    ajenti.feedback.start()
    ajenti.ipc.IPCServer.get().start()
    ajenti.licensing.Licensing.get()

    ajenti.server.serve_forever()

    if hasattr(ajenti.server, 'restart_marker'):
        logging.warn('Restarting by request')

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
    logging.error('Please submit it to https://github.com/ajenti/ajenti/issues/new')
