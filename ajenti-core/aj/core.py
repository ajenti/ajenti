from __future__ import unicode_literals

from aj.util import LazyModule
psutil = LazyModule('psutil') # -2MB

import daemon
import locale
import logging
import os
import signal
import socket
import sys
import syslog
import ssl
import traceback

import aj
import aj.plugins
from aj.auth import AuthenticationService
from aj.http import HttpRoot, HttpMiddlewareAggregator
from aj.gate.middleware import GateMiddleware
from aj.plugins import *
from aj.api import *
from aj.util import make_report
from aj.util.sslsocket import SSLSocket
from aj.util.pidfile import PidFile
from aj.wsgi import RequestHandler

import gevent
import gevent.ssl
from gevent import monkey
from OpenSSL import SSL, crypto

# Gevent monkeypatch ---------------------
monkey.patch_all(select=True, thread=True, aggressive=False, subprocess=True)

from gevent.event import Event
import threading
threading.Event = Event
# ----------------------------------------

import aj.compat

from socketio.server import SocketIOServer


def run(config=None, plugin_providers=[], product_name='ajenti', dev_mode=False, debug_mode=False, autologin=False):
    if config is None:
        raise TypeError('`config` can\'t be None')

    reload(sys)
    sys.setdefaultencoding('utf8')

    aj.product = product_name
    aj.debug = debug_mode
    aj.dev = dev_mode
    aj.dev_autologin = autologin

    aj.init()
    aj.log.set_log_params(tag='master', master_pid=os.getpid())
    aj.context = Context()
    aj.config = config
    aj.plugin_providers = plugin_providers
    logging.info('Loading config from %s' % aj.config)
    aj.config.load()

    if aj.debug:
        logging.warn('Debug mode')
    if aj.dev:
        logging.warn('Dev mode')

    try:
        locale.setlocale(locale.LC_ALL, '')
    except:
        logging.warning('Couldn\'t set default locale')

    logging.info('Ajenti Core %s' % aj.version)
    logging.info('Detected platform: %s / %s' % (aj.platform, aj.platform_string))

    # Load plugins
    PluginManager.get(aj.context).load_all_from(aj.plugin_providers)
    if len(PluginManager.get(aj.context).get_all()) == 0:
        logging.warn('No plugins were loaded!')

    if aj.config.data['bind']['mode'] == 'unix':
        path = aj.config.data['bind']['socket']
        if os.path.exists(path):
            os.unlink(path)
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            listener.bind(path)
        except:
            logging.error('Could not bind to %s' % path)
            sys.exit(1)

    if aj.config.data['bind']['mode'] == 'tcp':
        host = aj.config.data['bind']['host']
        port = aj.config.data['bind']['port']
        listener = socket.socket(socket.AF_INET6 if ':' in host else socket.AF_INET, socket.SOCK_STREAM)
        if not aj.platform in ['freebsd', 'osx']:
            try:
                listener.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
            except:
                logging.warn('Could not set TCP_CORK')
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logging.info('Binding to [%s]:%s' % (host, port))
        try:
            listener.bind((host, port))
        except Exception, e:
            logging.error('Could not bind: %s' % str(e))
            sys.exit(1)

    # Fix stupid socketio bug (it tries to do *args[0][0])
    socket.socket.__getitem__ = lambda x, y: None

    listener.listen(10)

    gateway = GateMiddleware.get(aj.context)
    application = HttpRoot(HttpMiddlewareAggregator([gateway])).dispatch

    aj.server = SocketIOServer(
        listener,
        log=open(os.devnull, 'w'),
        application=application,
        handler_class=RequestHandler,
        policy_server=False,
        transports=[
            str('websocket'),
            str('flashsocket'),
            str('xhr-polling'),
            str('jsonp-polling'),
        ],
    )

    if aj.config.data['ssl']['enable'] and aj.config.data['bind']['mode'] == 'tcp':
        try:
            context = SSL.Context(SSL.TLSv1_2_METHOD)
        except:
            context = SSL.Context(SSL.TLSv1_METHOD)
        context.set_session_id(str(id(context)))
        context.set_options(SSL.OP_NO_SSLv2 | SSL.OP_NO_SSLv3)
        context.set_cipher_list('ALL:!ADH:!EXP:!LOW:!RC2:!3DES:!SEED:!RC4:+HIGH:+MEDIUM')

        certificate = crypto.load_certificate(
            crypto.FILETYPE_PEM,
            open(aj.config.data['ssl']['certificate']).read()
        )
        private_key = crypto.load_privatekey(
            crypto.FILETYPE_PEM,
            open(aj.config.data['ssl']['certificate']).read()
        )

        context.use_certificate(certificate)
        context.use_privatekey(private_key)

        if aj.config.data['ssl']['client_auth']['enable']:
            # todo harden files
            logging.info('Enabling SSL client authentication')
            context.add_client_ca(certificate)
            context.get_cert_store().add_cert(certificate)
            verify_flags = SSL.VERIFY_PEER
            if aj.config.data['ssl']['client_auth']['force']:
                verify_flags |= SSL.VERIFY_FAIL_IF_NO_PEER_CERT
            context.set_verify(verify_flags, AuthenticationService.get(aj.context).client_certificate_callback)
            context.set_verify_depth(0)

        aj.server.ssl_args = {'server_side': True}
        aj.server.wrap_socket = lambda socket, **ssl: SSLSocket(context, socket)
        logging.info('SSL enabled')

    # auth.log
    try:
        syslog.openlog(
            ident=str(aj.product),
            facility=syslog.LOG_AUTH,
        )
    except:
        syslog.openlog(aj.product)

    def cleanup():
        if hasattr(cleanup, '_started'):
            return
        cleanup._started = True
        logging.info('Process %s exiting normally' % os.getpid())
        gevent.signal(signal.SIGINT, lambda: None)
        gevent.signal(signal.SIGTERM, lambda: None)
        if aj.master:
            gateway.destroy()

        p = psutil.Process(os.getpid())
        for c in p.children(recursive=True):
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

    aj.server.serve_forever()

    if not aj.master:
        # child process, server is stopped, wait until killed
        gevent.wait()
        #while True:
        #    gevent.sleep(3600)

    if hasattr(aj.server, 'restart_marker'):
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
        if aj.master:
            logging.debug('Server stopped')


def handle_crash(exc):
    # todo rework this
    logging.error('Fatal crash occured')
    traceback.print_exc()
    exc.traceback = traceback.format_exc(exc)
    report_path = '/root/%s-crash.txt' % aj.product
    try:
        report = open(report_path, 'w')
    except:
        report_path = './%s-crash.txt' % aj.product
        report = open(report_path, 'w')
    report.write(make_report(exc))
    report.close()
    logging.error('Crash report written to %s' % report_path)
    #logging.error('Please submit it to https://github.com/Eugeny/ajenti/issues/new')


def start(daemonize=False, log_level=logging.INFO, **kwargs):
    if daemonize:
        aj.log.init_log_directory()
        logfile = open(aj.log.LOG_FILE, 'w+')
        context = daemon.DaemonContext(
            pidfile=PidFile('/var/run/ajenti.pid'),
            stdout=logfile,
            stderr=logfile,
            detach_process=True
        )
        with context:
            gevent.reinit()
            aj.log.init_log_rotation()
            try:
                run(**kwargs)
            except Exception as e:
                handle_crash(e)
    else:
        try:
            run(**kwargs)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            handle_crash(e)

