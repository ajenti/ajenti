import gevent
from gevent.pywsgi import WSGIServer, WSGIHandler
import logging
import os
import socket
import threading
import traceback

from ajenti.api import *
from ajenti.plugins import manager
from ajenti.util import public


@public
@rootcontext
@interface
class IPCHandler (object):
    """
    Interface for custom IPC endpoints
    """

    def get_name(self):
        """
        Should return short identifier of IPC endpoint:

        $ ajenti-ipc <endpoint-name> <args>

        :rtype str:
        """

    def handle(self, args):
        """
        Override to handle IPC requests

        :param args: list of `str` parameters
        :type  args: list
        """


class IPCWSGIHandler (WSGIHandler):
    def __init__(self, *args, **kwargs):
        WSGIHandler.__init__(self, *args, **kwargs)
        self.client_address = ('ipc', 0)

    def log_request(self):
        pass


class IPCSocketServer (WSGIServer):
    pass


def ipc_application(environment, start_response):
    name, args = environment['PATH_INFO'].split('/')
    args = args.decode('base64').splitlines()
    logging.info('IPC: %s %s' % (name, args))

    for h in IPCHandler.get_all(manager.context):
        if h.get_name() == name:
            try:
                result = h.handle(args)
                if result is None:
                    start_response('404 Not found', [])
                    return ''
                else:
                    start_response('200 OK', [])
                    return result
            except Exception as e:
                traceback.print_exc()
                start_response('500 Error', [])
                return str(e)
            break
    else:
        start_response('404 Handler not found', [])


@public
@plugin
@persistent
@rootcontext
class IPCServer (BasePlugin):
    def start(self):
        gevent.spawn(self.run)

    def run(self):
        socket_path = '/var/run/ajenti-ipc.sock'
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if os.path.exists(socket_path):
            os.unlink(socket_path)
        sock.bind(socket_path)
        sock.listen(5)
        os.chmod(socket_path, 0700)

        server = IPCSocketServer(sock, application=ipc_application, handler_class=IPCWSGIHandler)
        server.serve_forever()
