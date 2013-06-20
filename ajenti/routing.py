import socketio

from ajenti.http import HttpHandler
from ajenti.api import BasePlugin
from ajenti.api.http import HttpPlugin, SocketPlugin
from ajenti.plugins import manager
from ajenti.profiler import *


class SocketIORouteHandler (HttpHandler):
    def __init__(self):
        self.namespaces = {}
        for cls in SocketPlugin.get_classes():
            self.namespaces[cls.name] = cls

    def handle(self, context):
        return socketio.socketio_manage(context.env, self.namespaces, context)


class InvalidRouteHandler (HttpHandler):
    def handle(self, context):
        context.respond_not_found()
        return 'Invalid URL'


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

        for instance in HttpPlugin.get_all():
            output = instance.handle(context)
            if output is not None:
                return output
        return context.fallthrough(self.invalid)
