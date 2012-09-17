from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins import *


info = PluginInfo(
	title = 'Test Plugin',
	dependencies = [
		#PluginDependency('ads')
	],
)

@interface
class TestIface (object):
	def test():
		pass


@plugin
class TestPlugin (TestIface, HttpPlugin):
	def test(self):
		print 'test'

	@url('/.+')
	def handle(self, context):
		context.respond_ok()
		return 'lol %s' % context

