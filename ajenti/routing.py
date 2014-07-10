import cgi
import socketio
import traceback

from ajenti.http import HttpHandler
from ajenti.api import BasePlugin, plugin, persistent, rootcontext
from ajenti.api.http import HttpPlugin, SocketPlugin
from ajenti.plugins import manager
from ajenti.profiler import *


class SocketIORouteHandler (HttpHandler):
    def __init__(self):
        self.namespaces = {}
        for cls in SocketPlugin.get_classes():
            self.namespaces[cls.name] = cls

    def handle(self, context):
        return str(socketio.socketio_manage(context.env, self.namespaces, context))


class InvalidRouteHandler (HttpHandler):
    def handle(self, context):
        context.respond_not_found()
        return 'Invalid URL'


@plugin
@persistent
@rootcontext
class CentralDispatcher (BasePlugin, HttpHandler):
    def __init__(self):
        self.invalid = InvalidRouteHandler()
        self.io = SocketIORouteHandler()

    @profiled(lambda a, k: 'HTTP %s' % a[1].path)
    def handle(self, context):
        """
        Dispatch the request to every HttpPlugin
        """

        if hasattr(context.session, 'appcontext'):
            self.context = context.session.appcontext
        else:
            self.context = manager.context

        if context.path.startswith('/ajenti:socket'):
            return context.fallthrough(self.io)

        if not hasattr(self.context, 'http_handlers'):
            self.context.http_handlers = HttpPlugin.get_all()

        for instance in self.context.http_handlers:
            try:
                output = instance.handle(context)
            except Exception as e:
                return [self.respond_error(context, e)]
            if output is not None:
                return output
        return context.fallthrough(self.invalid)

    def respond_error(self, context, exception):
        context.respond_server_error()
        stack = traceback.format_exc()
        return """
        <html>
            <body>

                <style>
                    body {
                        font-family: sans-serif;
                        color: #888;
                        text-align: center;
                    }

                    body pre {
                        width: 600px;
                        text-align: left;
                        margin: auto;
                        font-family: monospace;
                    }
                </style>

                <img src="/ajenti:static/main/error.jpeg" />
                <br/>
                <p>
                    Server error
                </p>
                <pre>
%s
                </pre>
            </body>
        </html>
        """ % cgi.escape(stack)
