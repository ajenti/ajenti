import re

from ajenti.http import HttpHandler
from ajenti.api.http import HttpPlugin


class InvalidRouteHandler (HttpHandler):
	def handle(self, context):
		context.respond_not_found()
		return 'Invalid URL'


class CentralDispatcher	(HttpHandler):
	def __init__(self):
		self.invalid = InvalidRouteHandler()

	def handle(self, context):
		for instance in HttpPlugin.get_all():
			output = instance.handle(context)
			if context.response_ready:
				return output
		return context.fallthrough(self.invalid)
		