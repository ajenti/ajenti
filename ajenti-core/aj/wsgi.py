import aj
import gevent.ssl
from geventwebsocket.handler import WebSocketHandler
from aj.security.verifier import ClientCertificateVerificator
from OpenSSL import crypto

class RequestHandler(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        WebSocketHandler.__init__(self, *args, **kwargs)

    def get_environ(self):
        env = WebSocketHandler.get_environ(self)
        env['SSL'] = isinstance(self.socket, gevent.ssl.SSLSocket)
        env['SSL_CLIENT_AUTH_FORCE'] = aj.config.data['ssl']['client_auth']['force']
        env['SSL_CLIENT_VALID'] = False
        env['SSL_CLIENT_USER'] = None
        if env['SSL']:
            peer_cert = self.socket.getpeercert(True)
            if peer_cert:
                certificate = crypto.load_certificate(crypto.FILETYPE_PEM, gevent.ssl.DER_cert_to_PEM_cert(peer_cert))
                env['SSL_CLIENT_CERTIFICATE'] = certificate
                if certificate:
                    user = ClientCertificateVerificator.get(aj.context).verify(certificate)
                    env['SSL_CLIENT_VALID'] = bool(user)
                    env['SSL_CLIENT_USER'] = user
                    env['SSL_CLIENT_DIGEST'] = certificate.digest('sha1')
        return env

    def _sendall(self, data):
        if isinstance(data, str):
                data = data.encode('utf-8')
        return WebSocketHandler._sendall(self, data)
