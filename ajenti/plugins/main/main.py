import os

from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins import manager


@plugin
class MainServer (BasePlugin, HttpPlugin):

	@url('/')
	def handle_static(self, context):
		context.respond_ok()
		return self.open_content('static/index.html').read()
		