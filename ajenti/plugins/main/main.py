import os
import json

from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins import manager
from ajenti.ui import UI, UIElement


@plugin
class MainServer (BasePlugin, HttpPlugin):

	@url('/')
	def handle_static(self, context):
		context.respond_ok()
		return self.open_content('static/index.html').read()
		

@plugin
class MainSocket (BasePlugin, SocketPlugin):
	name = '/stream'

	def on_connect(self, session):
		ui = UI()
		session.data['ui'] = ui
		ui.root = ui.create('main.page')
		self.send_ui(session)

	def on_message(self, session, message):
		pass

	def send_ui(self, session):
		data = json.dumps(session.data['ui'].render())
		self.emit('ui', data)


@plugin
class MainPageElement (UIElement):
	id = 'main.page'