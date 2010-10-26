import sys
import os
import logging

from twisted.web import server
from twisted.internet import reactor, ssl
from twisted.web.wsgi import WSGIResource

from ajenti.config import Config
from ajenti.core import AppDispatcher
from ajenti.plugmgr import load_plugins
import ajenti.utils



def run_server(log_level=logging.INFO, config_file=''):
    # Initialize logging subsystem
    log = logging.getLogger('ajenti')
    log.setLevel(log_level)
    stderr = logging.StreamHandler()
    stderr.setLevel(log_level)
    if log_level == logging.DEBUG:
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(module)s.%(funcName)s(): %(message)s')
    else:
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    stderr.setFormatter(formatter)
    log.addHandler(stderr)

    # Read config
    config = Config()
    if config_file:
        log.info('Using config file %s'%config_file)
        config.load(config_file)
    else:
        log.info('Using default settings')

    # Add log handler to config, so all plugins could access it
    config.set('log_facility',log)
    ajenti.utils.logger = log
    
    # Load external plugins
    load_plugins(config.get('ajenti', 'plugins'), log)

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

    if config.getint('ajenti', 'ssl') == 1:
        ssl_context = ssl.DefaultOpenSSLContextFactory(
    	    config.get('ajenti','cert_file'), 
    	    config.get('ajenti','cert_file')
        )
        reactor.listenSSL(
        	port,
        	site,
        	contextFactory = ssl_context,
        )
    else:
        reactor.listenTCP(port, site)

    reactor.run()

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
        
