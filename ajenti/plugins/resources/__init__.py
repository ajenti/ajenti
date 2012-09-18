from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
	title = 'Resources Manager',
	dependencies = [
	],
)

def init():
	import server

