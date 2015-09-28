import gevent
import logging
import re
import six
import types
from jadi import interface


def url(pattern):
    """
    Exposes the decorated method of your :class:`HttpPlugin` via HTTP

    :param pattern: URL regex (``^`` and ``$`` are implicit)
    :type  pattern: str
    :rtype: function

        Named capture groups will be fed to function as ``**kwargs``

    """

    def decorator(f):
        f.url_pattern = re.compile('^%s$' % pattern)
        return f
    return decorator


class BaseHttpHandler(object):
    """
    Base class for everything that can process HTTP requests
    """

    def handle(self, http_context):
        """
        Should create a HTTP response in the given ``http_context`` and return
        the plain output

        :param http_context: HTTP context
        :type  http_context: :class:`aj.http.HttpContext`
        """


@interface
class HttpMiddleware(BaseHttpHandler):
    def __init__(self, context):
        self.context = context

    def handle(self, http_context):
        pass


@interface
class HttpPlugin(object):
    """
    A base interface for HTTP request handling::

        @component
        class HelloHttp(HttpPlugin):
            @url('/hello/(?P<name>.+)')
            def get_page(self, http_context, name=None):
                context.add_header('Content-Type', 'text/plain')
                context.respond_ok()
                return 'Hello, %s!' % name

    """

    def __init__(self, context):
        self.context = context

    def handle(self, http_context):
        """
        Finds and executes the handler for given request context (handlers are
        methods decorated with :func:`url` )

        :param http_context: HTTP context
        :type  http_context: :class:`aj.http.HttpContext`
        :returns: reponse data
        """

        for name, method in six.iteritems(self.__class__.__dict__):
            if hasattr(method, 'url_pattern'):
                method = getattr(self, name)
                match = method.url_pattern.match(http_context.path)
                if match:
                    http_context.route_data = match.groupdict()
                    data = method(http_context, **http_context.route_data)
                    if isinstance(data, six.text_type):
                        data = data.encode('utf-8')
                    if isinstance(data, types.GeneratorType):
                        return data
                    else:
                        return [data]


@interface
class SocketEndpoint(object):
    """
    Base interface for Socket.IO endpoints.

    """

    plugin = None
    """arbitrary plugin ID for socket message routing"""

    def __init__(self, context):
        self.context = context
        self.greenlets = []

    def on_connect(self, message):
        """
        Called on a successful client connection
        """

    def on_disconnect(self, message):
        """
        Called on a client disconnect
        """

    def destroy(self):
        """
        Destroys endpoint, killing the running greenlets
        """
        for gl in self.greenlets:
            gl.kill(block=False)

    def on_message(self, message, *args):
        """
        Called when a socket message arrives to this endpoint
        """

    def spawn(self, target, *args, **kwargs):
        """
        Spawns a greenlet in this endpoint, which will be auto-killed when the client disconnects

        :param target: target function
        """
        logging.debug(
            'Spawning sub-Socket Greenlet (in a namespace): %s' % (
                target.__name__
            )
        )
        greenlet = gevent.spawn(target, *args, **kwargs)
        self.greenlets.append(greenlet)
        return greenlet

    def send(self, data, plugin=None):
        """
        Sends a message to the client.the

        :param data: message object
        :param plugin: routing ID (this endpoint's ID if not specified)
        :type  plugin: str
        """
        self.context.worker.send_to_upstream({
            'type': 'socket',
            'message': {
                'plugin': plugin or self.plugin,
                'data': data,
            },
        })
