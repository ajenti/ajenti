from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
	title = 'NGINX',
	dependencies = [
		PluginDependency('main')
	],
)

def init():
	import configurator

