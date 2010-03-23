# -*- coding: utf-8 -*-
#
 
import sys
import logging
from wsgiref.simple_server import make_server, WSGIRequestHandler, WSGIServer
from OpenSSL import SSL
import socket

from ajenti.config import Config
from ajenti.app import AppDispatcher
import ajenti.app.plugins as plugins
 
class SecureRequestHandler(WSGIRequestHandler):
    def setup(self):
        self.connection = self.request
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)
		
class SecureServer(WSGIServer):
    cert_file = ''
    
    def __init__(self, server_address, HandlerClass):
        WSGIServer.__init__(self, server_address, HandlerClass)
#        import ssl
#        self.socket = ssl.wrap_socket(socket.socket(self.address_family,self.socket_type), 
#                        keyfile=SecureServer.cert_file,
#                        certfile=SecureServer.cert_file, 
#                        server_side=True, 
#                        ssl_version=ssl.PROTOCOL_SSLv3,
#                        do_handshake_on_connect=True)
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.use_privatekey_file(SecureServer.cert_file)
        ctx.use_certificate_file(SecureServer.cert_file)
        self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
                                                        self.socket_type))
        self.server_bind()
        self.server_activate()

        
def server():
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
    config.set('log_facility',log)

    # Load external plugins
    plugins.loader(config.get('ajenti', 'plugins'))

    # Start server
    if config.getint('ajenti', 'ssl') == 1:
        SecureServer.cert_file = config.get('ajenti','cert_file')
        httpd = make_server(host, port, AppDispatcher(config).dispatcher, SecureServer, SecureRequestHandler)
        #httpd = make_server(host, port, AppDispatcher(config).dispatcher, SecureServer)
    else:
        httpd = make_server(host, port, AppDispatcher(config).dispatcher)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt, e:
        log.warn('Stopping by <Control-C>') 
        
     
