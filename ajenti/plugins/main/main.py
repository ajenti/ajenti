import os
import json

from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins import manager
from ajenti.ui import *

from api import SectionPlugin


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
		if not 'ui' in session.data:
			ui = UI()
			session.data['ui'] = ui
			ui.root = MainPage()
			ui.root.append(SectionsRoot())

		self.send_ui(session)

	def on_message(self, session, message):
		ui = session.data['ui']
		if message['type'] == 'ui_update':
			for update in message['content']:
				if update['type'] == 'event':
					ui.dispatch_event(update['_'], update['event'], update['params'])

	def send_ui(self, session):
		data = json.dumps(session.data['ui'].render())
		self.emit('ui', data)


@plugin
class MainPage (UIElement):
	id = 'main:page'


@plugin
class SectionsRoot (UIElement):
	id = 'main:sections_root'

	def init(self):
		for cls in SectionPlugin.get_classes():
			cat = cls.new()
			self.append(cat)

