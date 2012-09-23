import re
import json
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin

import ajenti
from ajenti.api import interface


def url(pattern):
    def decorator(f):
        f._url_pattern = re.compile('^%s$' % pattern)
        return f
    return decorator


@interface
class HttpPlugin (object):
    def handle(self, context):
        for name, method in self.__class__.__dict__.iteritems():
            if hasattr(method, '_url_pattern'):
                method = getattr(self, name)
                match = method._url_pattern.match(context.path)
                if match:
                    context.route_data = match.groupdict()
                    return method(context, **context.route_data)


@interface
class SocketPlugin (BaseNamespace, RoomsMixin, BroadcastMixin):
    name = None

    def __init__(self, *args, **kwargs):
        if self.name is None:
            raise Exception('Socket name is not set')
        BaseNamespace.__init__(self, *args, **kwargs)

    def recv_connect(self):
        if self.request.session.identity is None:
            return 
            
        self.socket.session = self.request.session
        self.on_connect()

    def recv_disconnect(self):
        if self.request.session.identity is None:
            return 
            
        self.on_disconnect()
        self.disconnect(silent=True)

    def recv_message(self, message):
        if self.request.session.identity is None:
            return 
            
        self.socket.session.touch()
        self.on_message(json.loads(message))

    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_message(self, message):
        pass

