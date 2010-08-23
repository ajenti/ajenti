from ajenti.ui import *
from ajenti.app.helpers import ModuleContent

class UzuriMaster:
    remotes = []

    def __init__(self):
	self.remotes = ['localhost:8001', 'localhost:8002', 'nowhere:8000']

    def get_sidepane(self):
	c = UI.VContainer(UI.RemoteAllButton())
	for r in self.remotes:
	    c.vnode(UI.RemoteHostButton(id=r, addr=r))
	return c

    def get_mainpane(self):
	c = UI.Container(width='100%', height='100%')
	for r in self.remotes:
	    c.appendChild(UI.RemoteView(id=r, addr=r+'/handle///'))
	return c


class UzuriContent(ModuleContent):
    module = 'uzuri_master'
    path = __file__
    js_files = ['uzuri.js']
    css_files = ['uzuri.css']
    widget_files = ['widgets.xml']
