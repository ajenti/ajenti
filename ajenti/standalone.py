# -*- coding: utf-8 -*-
#
 
import sys
import logging
from wsgiref.simple_server import make_server

from ajenti.config import Config
from ajenti.app import AppDispatcher

def simple_server():
    # Initialize logging subsystem
    log = logging.getLogger('ajenti')
    stderr = logging.StreamHandler()
    stderr.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(name)s: %(levelname)-8s %(module)s.%(funcName)s(): %(message)s')
    stderr.setFormatter(formatter)
    log.addHandler(stderr)

    # Read config
    config = Config()
    # config.read('/etc/ajenti/ajenti.conf')
    host = config.get('ajenti','bind_host')
    port = config.getint('ajenti','bind_port')
    # Add log handler to config, so all plugins could access it
    config.set('ajenti','log_facility',log)

    # Start server
    httpd = make_server(host, port, AppDispatcher(config).dispatcher)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt, e:
        log.warn('Stopping by <Control-C>') 
     
