import re


class HttpRoot:
	def __init__(self, stack=[]):
		self.stack = stack

	def add(self, middleware):
		self.stack.append(middleware)

	def dispatch(self, env, start_response):
		context = HttpContext(env, start_response)
		for middleware in stack:
			output = middleware.handle(context)
			if context.response_ready:
				return output


class HttpContext:
	def __init__(self, env, start_response):
		self.start_response = start_response
		self.env = env
		self.path = env['PATH_INFO']
		self.headers = []
		self.respone_ready = False

	def add_header(self, key, value):
		self.headers += [(key, value)]

	def respond(self, status):
		self.start_response(status, self.headers)
		self.respone_ready = True

	def respond_ok(self):
		self.respond('200 OK')

	def respond_server_error(self):
		self.respond('500 Server Error')

	def respond_forbidden(self):
		self.respond('403 Forbidden')

	def respond_not_found(self):
		self.respond('404 Not Found')


class HttpHandler:
	def handle(self, context):
		pass
