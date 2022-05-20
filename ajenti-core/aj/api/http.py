import gevent
import logging
import re
import types
from jadi import interface


def url(pattern):
    """
    Exposes the decorated method of your :class:`HttpPlugin` via HTTP.
    Will be deprecated in favor of new decorators ( @get, @post, ... )

    :param pattern: URL regex (``^`` and ``$`` are implicit)
    :type  pattern: str
    :rtype: function

        Named capture groups will be fed to function as ``**kwargs``

    """

    def decorator(f):
        f.url_pattern = re.compile(f'^{pattern}$')
        return f
    return decorator

def requests_decorator_generator(method):
    """
    Factorization to generate request decorators like @get or @post.

    :param method: Request method decorator to generate, like get or post
    :type method: basestring
    :return:
    :rtype:
    """

    def request_decorator(pattern):
        """
        Exposes the decorated method of your :class:`HttpPlugin` via HTTP

        :param pattern: URL regex (``^`` and ``$`` are implicit)
        :type  pattern: str
        :rtype: function

            Named capture groups will be fed to function as ``**kwargs``

        """

        def decorator(f):
            # Request method involved, like get or post
            f.method = method
            f.url_pattern = re.compile(f'^{pattern}$')
            return f
        return decorator

    return request_decorator

# Decorators like @get and @post are defined here
for method in ['get', 'post', 'delete', 'head', 'put', 'patch']:
    globals()[method] = requests_decorator_generator(method)

class BaseHttpHandler():
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
class HttpMasterMiddleware(BaseHttpHandler):
    def __init__(self, context):
        self.context = context

    def handle(self, http_context):
        pass

@interface
class HttpPlugin():
    """
    A base interface for HTTP request handling::

        @component
        class HelloHttp(HttpPlugin):
            @get('/hello/(?P<name>.+)')
            def get_page(self, http_context, name=None):
                context.add_header('Content-Type', 'text/plain')
                context.respond_ok()
                return 'Hello, f"{name}"!'

    """

    def __init__(self, context):
        self.context = context

    def handle(self, http_context):
        """
        Finds and executes the handler for given request context
        (handlers were methods decorated with :func:`url` and will be
        decorated with e.g. @get and @post in the future)

        :param http_context: HTTP context
        :type  http_context: :class:`aj.http.HttpContext`
        :returns: reponse data
        """

        for name, handle_function in self.__class__.__dict__.items():
            if hasattr(handle_function, 'url_pattern'):
                handle_function = getattr(self, name)
                match = handle_function.url_pattern.match(http_context.path)
                if match:
                    if hasattr(handle_function, 'method'):
                        # Check if the requested method is supported by the
                        # function, e.g. avoid accept a get request in a post method
                        if handle_function.method == http_context.method.lower():
                            http_context.route_data = match.groupdict()
                            data = handle_function(http_context, **http_context.route_data)
                            if isinstance(data, str):
                                data = data.encode('utf-8')
                            if isinstance(data, types.GeneratorType):
                                return data

                            return [data]
                    else:
                        # Ensure compatibility with old @url decorator
                        logging.warning(f'Backward @url compatibility for {handle_function.__name__}')
                        http_context.route_data = match.groupdict()
                        data = handle_function(http_context, **http_context.route_data)
                        if isinstance(data, str):
                            data = data.encode('utf-8')
                        if isinstance(data, types.GeneratorType):
                            return data

                        return [data]


@interface
class SocketEndpoint():
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
            f'Spawning sub-Socket Greenlet (in a namespace): {target.__name__}'
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
