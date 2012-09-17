import re

from ajenti.http import HttpHandler


class Dispatcher (HttpHandler):
	def __init__(self):
		self.routes = []

	def handle(self, context):
		for route in self.routes:
			match = route[0].match(env['PATH_INFO'])
			if match:
				print match.groups()
				return route[1].handle(context)

	def route(self, url, handler):
		self.routes += [(re.compile(url), handler)]


# ---------------
# Implementations
# ---------------

class InvalidRouteHandler (HttpHandler):
	def handle(self, context):
		context.respond_not_found()
		return 'Invalid URL'


class CentralDispatcher	(Dispatcher):
	def __init__(self):
		Dispatcher.__init__(self)
		self.route(r'/(?P<path>.+)/(?P<pathb>.+)', InvalidRouteHandler())
		self.route(r'.+', InvalidRouteHandler())
