from socketio.handler import SocketIOHandler

from aj.util.sslsocket import SSLSocket


class RequestHandler (SocketIOHandler):
    def __init__(self, *args, **kwargs):
        SocketIOHandler.__init__(self, *args, **kwargs)
        self.server.resource = 'socket.io'

    def get_environ(self):
        env = SocketIOHandler.get_environ(self)
        env['SSL'] = isinstance(self.socket, SSLSocket)
        env['SSL_VALID'] = False
        env['SSL_CN'] = None
        if env['SSL']:
            env['SSL_CERTIFICATE'] = self.socket.get_peer_certificate()
            if env['SSL_CERTIFICATE']:
                # TODO handle openssl cert
                env['SSL_VALID'] = 'subject' in env['SSL_CERTIFICATE']
                if env['SSL_VALID']:
                    for subj in env['SSL_CERTIFICATE']['subject']:
                        k, v = subj[0]
                        if k == 'commonName':
                            env['SSL_CN'] = v
        return env

    def handle_one_response(self):
        path = self.environ.get('PATH_INFO')
        prefix = self.environ.get('HTTP_X_URL_PREFIX', '')
        self.server.resource = (prefix + '/socket.io').strip('/')
        response = SocketIOHandler.handle_one_response(self)
        self.server.resource = 'socket.io'
        return response
