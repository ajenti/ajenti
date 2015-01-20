import gevent
import json
import logging
import re
import types

from aj.api import *


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


class BaseHttpHandler (object):
    """
    Base class for everything that can process HTTP requests
    """

    def handle(self, context):
        """
        Should create a HTTP response in the given ``context`` and return the plain output

        :param context: HTTP context
        :type  context: :class:`aj.http.HttpContext`
        """


@interface
class HttpPlugin (object):
    """
    A base plugin class for HTTP request handling::

        @plugin
        class TerminalHttp (BasePlugin, HttpPlugin):
            @url('/aj:terminal/(?P<id>\d+)')
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
        :type  context: :class:`aj.http.HttpContext`
        """

        for name, method in self.__class__.__dict__.iteritems():
            if hasattr(method, '_url_pattern'):
                method = getattr(self, name)
                match = method._url_pattern.match(context.path)
                if match:
                    context.route_data = match.groupdict()
                    data = method(context, **context.route_data)
                    if isinstance(data, types.GeneratorType):
                        return data
                    else:
                        return [data]


@interface
class SocketEndpoint (object):
    plugin = None

    def __init__(self, context):
        self.context = context
        self.greenlets = []

    def on_connect(self, message):
        pass

    def on_disconnect(self, message):
        pass

    def destroy(self):
        for gl in self.greenlets:
            gl.kill(block=False)

    def on_message(self, message, *args):
        pass

    def spawn(self, target, *args, **kwargs):
        logging.debug('Spawning sub-Socket Greenlet (in a namespace): %s' % target.__name__)
        greenlet = gevent.spawn(target, *args, **kwargs)
        self.greenlets.append(greenlet)
        return greenlet

    def send(self, data, plugin=None):
        self.context.worker.send_to_upstream({
            'type': 'socket',
            'message': {
                'plugin': plugin or self.plugin,
                'data': data,
            },
        })
