from ajenti.ui import *
from ajenti.app.helpers import ModuleContent, SessionPlugin
from uzuri.api import *


class IUzuriMaster(Interface):
    pass

class UzuriMaster(SessionPlugin):
    implements(IUzuriMaster)
    remotes = []

    def on_session_start(self):
	self._cookies = {}

    def init(self):
	self.remotes = ['localhost:8001', 'localhost:8002', 'nowhere:8000']

    def get_ui_plugins(self):
	c = UI.Container()
	plugins = self.app.grab_plugins(IClusteredPlugin)
	plugins = sorted(plugins, key=lambda x: x.get_name())
	for p in plugins:
	    c.appendChild(UI.RemotePluginButton(id=p.get_name(), name=p.text, icon=p.category['icon']))
	return c

    def get_ui_hosts(self):
	c = UI.Container(UI.RemoteAllButton())
	for r in self.remotes:
	    cookie = ""
	    if r in self._cookies:
		cookie = self._cookies[r]
	    c.appendChild(UI.RemoteHostButton(id=r, addr=r, cookie=cookie))
	return c

    def get_mainpane(self):
	c = UI.Container(width='100%', height='100%')
	for r in self.remotes:
	    c.appendChild(UI.RemoteView(id=r, addr=r+'/handle///'))
	return c


class UzuriContent(ModuleContent):
    module = 'uzuri_master'
    path = __file__
    js_files = ['core.js', 'ui.js']
    widget_files = ['widgets.xml']
