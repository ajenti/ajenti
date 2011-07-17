import sys
import os
import logging

from twisted.web import server
from twisted.internet import reactor, ssl
from twisted.web.wsgi import WSGIResource

from ajenti.api import ComponentManager
from ajenti.config import Config
from ajenti.core import Application, AppDispatcher
from ajenti.plugmgr import load_plugins
from ajenti import version
import ajenti.utils



class DebugHandler (logging.StreamHandler):
    def __init__(self):
        self.capturing = False
        self.buffer = ''

    def start(self):
        self.capturing = True

    def stop(self):
        self.capturing = False

    def handle(self, record):
        if self.capturing:
            self.buffer += self.formatter.format(record) + '\n'


def run_server(log_level=logging.INFO, config_file=''):
    # Initialize logging subsystem
    log = logging.getLogger('ajenti')
    log.setLevel(logging.DEBUG)

    stdout = logging.StreamHandler(sys.stdout)
    stdout.setLevel(log_level)
    log.blackbox = DebugHandler()
    log.blackbox.setLevel(logging.DEBUG)

    dformatter = logging.Formatter('%(asctime)s %(levelname)-8s %(module)s.%(funcName)s(): %(message)s')
    sformatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    stdout.setFormatter(dformatter if log_level == logging.DEBUG else sformatter)
    log.blackbox.setFormatter(dformatter)

    log.addHandler(log.blackbox)
    log.addHandler(stdout)

    # For the debugging purposes
    log.info('Ajenti %s' % version())

    # We need this early
    ajenti.utils.logger = log

    # Read config
    config = Config()
    if config_file:
        log.info('Using config file %s'%config_file)
        config.load(config_file)
    else:
        log.info('Using default settings')

    # Add log handler to config, so all plugins could access it
    config.set('log_facility',log)

    log.blackbox.start()

    # Load external plugins
    load_plugins(config.get('ajenti', 'plugins'), log)


    # Start components
    ComponentManager.create(Application(config))

    # Start server
    host = config.get('ajenti','bind_host')
    port = config.getint('ajenti','bind_port')
    log.info('Listening on %s:%d'%(host, port))

    resource = WSGIResource(
            reactor,
            reactor.getThreadPool(),
            AppDispatcher(config).dispatcher
    )

    site = server.Site(resource)
    config.set('server', reactor)

    log.info('Starting server')
    if config.getint('ajenti', 'ssl') == 1:
        ssl_context = ssl.DefaultOpenSSLContextFactory(
    	    config.get('ajenti','cert_key'),
    	    config.get('ajenti','cert_file')
        )
        reactor.listenSSL(
        	port,
        	site,
        	contextFactory = ssl_context,
        )
    else:
        reactor.listenTCP(port, site)


    log.blackbox.stop()

    reactor.run()

    ComponentManager.get().stop()

    if hasattr(reactor, 'restart_marker'):
        log.info('Restarting by request')

        fd = 20 # Close all descriptors. Creepy thing
        while fd > 2:
            try:
                os.close(fd)
                log.debug('Closed descriptor #%i'%fd)
            except:
                pass
            fd -= 1

        os.execv(sys.argv[0], sys.argv)
    else:
        log.info('Stopped by request')
