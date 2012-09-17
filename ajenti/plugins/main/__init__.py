from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
	title = 'Test Plugin',
	dependencies = [
		PluginDependency('ads')
	],
)

@interface
class TestIface:
	def test():
		pass


@plugin
class TestPlugin (TestIface):
	def test():
		print 'test'