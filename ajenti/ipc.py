import os
import threading
from SocketServer import UnixStreamServer
from BaseHTTPServer import BaseHTTPRequestHandler

from ajenti.api import *
from ajenti.plugins import manager
from ajenti.util import public


@public
@interface
class IPCHandler (object):
    """
    Interface for custom IPC endpoints
    """

    def get_name(self):
        """
        Should return short identifier of IPC endpoint:

        $ ajenti-ipc <endpoint-name> <args>
        """

    def handle(self, args):
        """
        Override to handle IPC requests

        :param args: list of `str` parameters
        """


class Handler (BaseHTTPRequestHandler):
    def do_GET(self):
        name, args = self.path.split('/')
        args = args.decode('base64').splitlines()
        for h in IPCHandler.get_all(manager.context):
            if h.get_name() == name:
                try:
                    result = h.handle(args)
                    self.send_response(200, 'OK')
                    self.end_headers()
                    self.wfile.write(result)
                except Exception, e:
                    self.send_response(500, 'Error')
                    self.end_headers()
                    self.wfile.write(str(e))
                break
        else:
            self.send_response(404, 'Handler not found')
            self.end_headers()
        self.wfile.close()

    def log_request(self, *args):
        pass


@public
@plugin
class IPCServer (BasePlugin):
    def start(self):
        t = threading.Thread(target=self.run)
        t.daemon = True
        t.start()

    def run(self):
        socket_path = '/var/run/ajenti-ipc.sock'
        if os.path.exists(socket_path):
            os.unlink(socket_path)

        server = UnixStreamServer(socket_path, Handler)
        os.chmod(socket_path, 0700)
        server.serve_forever()
