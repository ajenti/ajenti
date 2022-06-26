import aj
import gevent.ssl
from geventwebsocket.handler import WebSocketHandler
from aj.security.verifier import ClientCertificateVerificator
from OpenSSL import crypto

class RequestHandler(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        WebSocketHandler.__init__(self, *args, **kwargs)

    def run_application(self):
        """
        The WebSocketHandler class will test on each request if the header
        HTTP_UPGRADE is set to websocket. In this case, it will try to open a
        websocket connection, but in the other case, it just passes the request
        to his parent class.

        The problem is that it generates a lot of unnecessary debug log and I'm
        trying to avoid it by this simple trick.
        """

        upgrade = self.environ.get('HTTP_UPGRADE', '')
        if upgrade == 'websocket':
            # Pass it to WebSocketHandler
            super(RequestHandler, self).run_application()
        else:
            # Pass it to WSGIHandler from gevent.pywsgi
            super(WebSocketHandler, self).run_application()

    def get_environ(self):
        """
        Wrapper to handles client certificates and writes it to environ.
        """

        env = WebSocketHandler.get_environ(self)
        env['SSL'] = isinstance(self.socket, gevent.ssl.SSLSocket)
        env['SSL_CLIENT_AUTH_FORCE'] = (
            aj.config.data['ssl']['client_auth']['force']
            and
            aj.config.data['ssl']['client_auth']['enable']
        )
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
                    env['SSL_CLIENT_DIGEST'] = certificate.digest('sha256')
        return env

    def _sendall(self, data):
        """
        Wrapper to ensure utf-8 compatibility.
        """

        if isinstance(data, str):
                data = data.encode('utf-8')
        return WebSocketHandler._sendall(self, data)
