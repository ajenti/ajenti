from socketio.handler import SocketIOHandler
import six

import aj
from aj.util.sslsocket import SSLSocket
from aj.security.verifier import ClientCertificateVerificator


class RequestHandler(SocketIOHandler):
    def __init__(self, *args, **kwargs):
        SocketIOHandler.__init__(self, *args, **kwargs)
        self.server.resource = 'socket.io'

    def get_environ(self):
        env = SocketIOHandler.get_environ(self)
        env['SSL'] = isinstance(self.socket, SSLSocket)
        env['SSL_CLIENT_VALID'] = False
        env['SSL_CLIENT_USER'] = None
        if env['SSL']:
            certificate = self.socket.get_peer_certificate()
            env['SSL_CLIENT_CERTIFICATE'] = certificate
            if certificate:
                user = ClientCertificateVerificator.get(aj.context).verify(certificate)
                env['SSL_CLIENT_VALID'] = bool(user)
                env['SSL_CLIENT_USER'] = user
                env['SSL_CLIENT_DIGEST'] = certificate.digest('sha1')
        return env

    def handle_one_response(self):
        prefix = self.environ.get('HTTP_X_URL_PREFIX', '')
        self.server.resource = (prefix + '/socket.io').strip('/')
        response = SocketIOHandler.handle_one_response(self)
        self.server.resource = 'socket.io'
        return response

    def _sendall(self, data):
        data = six.binary_type(data) if data else data
        return SocketIOHandler._sendall(self, data)
