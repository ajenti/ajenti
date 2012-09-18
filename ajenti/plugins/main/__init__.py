from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins import *


info = PluginInfo(
	title = 'Test Plugin',
	dependencies = [
		#PluginDependency('ads')
	],
)

@plugin
class TestPlugin (HttpPlugin):
	@url('/test')
	def handle_test(self, context):
		context.respond_ok()
		return 'lol %s' % context

