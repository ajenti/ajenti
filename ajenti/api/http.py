import re
import json
import types

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin

from ajenti.api import BasePlugin, interface


def url(pattern):
    """
    Exposes the decorated method of your :class:`HttpPlugin` via HTTP

    :param pattern: URL regex (no ``^`` and ``$`` required)
    :type  pattern: str
    :rtype: function

        Named capture groups will be fed to function as ``**kwargs``

    """

    def decorator(f):
        f._url_pattern = re.compile('^%s$' % pattern)
        return f
    return decorator


@interface
class HttpPlugin (object):
    """
    A base plugin class for HTTP request handling::

        @plugin
        class TerminalHttp (BasePlugin, HttpPlugin):
            @url('/ajenti:terminal/(?P<id>\d+)')
            def get_page(self, context, id):
                if context.session.identity is None:
                    context.respond_redirect('/')
                context.add_header('Content-Type', 'text/html')
                context.respond_ok()
                return self.open_content('static/index.html').read()

    """

    def handle(self, context):
        """
        Finds and executes the handler for given request context (handlers are methods decorated with :func:`url` )

        :param context: HTTP context
        :type  context: :class:`ajenti.http.HttpContext`
        """

        for name, method in self.__class__.__dict__.iteritems():
            if hasattr(method, '_url_pattern'):
                method = getattr(self, name)
                match = method._url_pattern.match(context.path)
                if match:
                    context.route_data = match.groupdict()
                    data = method(context, **context.route_data)
                    if type(data) is types.GeneratorType:
                        return data
                    else:
                        return [data]


@interface
class SocketPlugin (BasePlugin, BaseNamespace, RoomsMixin, BroadcastMixin):
    """
    A base class for a Socket.IO endpoint::

        @plugin
        class TerminalSocket (SocketPlugin):
            name = '/terminal'

            def on_message(self, message):
                if message['type'] == 'select':
                    self.id = int(message['tid'])
                    self.terminal = self.context.session.terminals[self.id]
                    self.send_data(self.terminal.protocol.history())
                    self.spawn(self.worker)
                if message['type'] == 'key':
                    ch = b64decode(message['key'])
                    self.terminal.write(ch)

            ...
    """

    name = None
    """ Endpoint ID """

    def __init__(self, *args, **kwargs):
        if self.name is None:
            raise Exception('Socket endpoint name is not set')
        BaseNamespace.__init__(self, *args, **kwargs)

    def recv_connect(self):
        """ Internal """
        if self.request.session.identity is None:
            self.emit('auth-error', '')
            return

        self.context = self.request.session.appcontext
        self.on_connect()

    def recv_disconnect(self):
        """ Internal """
        if self.request.session.identity is None:
            return

        self.on_disconnect()
        self.disconnect(silent=True)

    def recv_message(self, message):
        """ Internal """
        if self.request.session.identity is None:
            return

        self.request.session.touch()
        self.on_message(json.loads(message))

    def on_connect(self):
        """ Called when a socket is connected """

    def on_disconnect(self):
        """ Called when a socket disconnects """

    def on_message(self, message):
        """
        Called when a message from browser arrives

        :param message: a message object (parsed JSON)
        :type  message: str
        """
