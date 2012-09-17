import logging
import signal
import syslog

import ajenti   
from ajenti.http import HttpRoot
from ajenti.routing import CentralDispatcher
from ajenti.middleware import SessionMiddleware, AuthenticationMiddleware
import ajenti.plugins


try:
    import gevent
    import gevent.pywsgi
    WSGIServer = gevent.pywsgi.WSGIServer
    http_server = 'gevent'
except ImportError:
    from wsgiref.simple_server import make_server
    WSGIServer = lambda addr,**kw : make_server(addr[0], addr[1], kw['application'])
    http_server = 'wsgiref'


def run():
    logging.info('Ajenti %s running on platform: %s' % (ajenti.version, ajenti.platform))

    # Setup webserver
    if 'bind' in ajenti.config:
        host = ajenti.config['bind']['host']
        port = ajenti.config['bind']['port']
    else:
        host = port = None

    logging.info('Listening on %s:%d' % (host, port))

    ssl = {}
    if 'ssl' in ajenti.config:
        if ajenti.config['ssl']['enable']:
            ssl = {
                'keyfile':  ajenti.config['ssl']['certificate_path'],
                'certfile': ajenti.config['ssl']['key_path'],
            }

    logging.info('Using HTTP server: %s' % http_server)

    stack = [SessionMiddleware(), AuthenticationMiddleware(), CentralDispatcher()]
    server = WSGIServer(
        (host, port),
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


    # Load plugins
    ajenti.plugins.manager.load_all()

    try:
        gevent.signal(signal.SIGTERM, lambda: sys.exit(0))
    except:
        pass
    
    server.serve_forever()