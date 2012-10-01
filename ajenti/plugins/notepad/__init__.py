from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
	title = 'Notepad',
	dependencies = [
		PluginDependency('main')
	],
)

def init():
	import notepad

