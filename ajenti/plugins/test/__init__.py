from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
	title = 'Test',
	dependencies = [
		PluginDependency('main')
	],
)

def init():
	import dash

