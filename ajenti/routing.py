import re
import socketio

from ajenti.http import HttpHandler
from ajenti.api.http import HttpPlugin, SocketPlugin


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


class CentralDispatcher	(HttpHandler):
	def __init__(self):
		self.invalid = InvalidRouteHandler()
		self.io = SocketIORouteHandler()

	def handle(self, context):
		if context.path.startswith('/socket.io'):
			return context.fallthrough(self.io)

		for instance in HttpPlugin.get_all():
			output = instance.handle(context)
			if context.response_ready:
				return output
		return context.fallthrough(self.invalid)
		