import os

from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins import manager


@plugin
class ContentServer (HttpPlugin):

	@url('/static/(?P<plugin>\w+)/(?P<path>.+)')
	def handle_static(self, context, plugin, path):
		plugin_path = manager.resolve_path(plugin)
		if plugin_path is None:
			context.respond_not_found()
			return 'Not Found'
		path = os.path.join(plugin_path, 'content/static', path)
		return context.file(path)

