import os
import re

from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins import manager


@plugin
class ContentServer (HttpPlugin):
	@url('/static/resources.(?P<type>.+)')
	def handle_compressed(self, context, type):
		content = ContentCompressor.get().compressed[type]
		return context.gzip(content)

	@url('/static/(?P<plugin>\w+)/(?P<path>.+)')
	def handle_static(self, context, plugin, path):
		plugin_path = manager.resolve_path(plugin)
		if plugin_path is None:
			context.respond_not_found()
			return 'Not Found'
		path = os.path.join(plugin_path, 'content/static', path)
		return context.file(path)


@plugin
class ContentCompressor (object):
	def __init__(self):
		self.files = {}
		self.compressed = {}
		self.compressors = {
			'js': self.process_js,
			'css': self.process_css
		}
		self.patterns = {
			'js': r'.+\.js$',
			'css': r'.+\.css$'
		}
		self.scan()
		self.compress()

	def scan(self):
		for plugin in manager.get_all():
			path = os.path.join(manager.resolve_path(plugin), 'content')
			if not os.path.exists(path):
				continue
			for name in os.listdir(path):
				for key in self.patterns:
					if re.match(self.patterns[key], name):
						self.files.setdefault(key, []).append(os.path.join(path, name))

	def compress(self):
		print self.files
		for key in self.patterns:
			self.compressed[key] = self.compressors[key](self.files.setdefault(key, []))

	def process_js(self, files):
		return '\n'.join([open(x).read() for x in files])
	
	def process_css(self, files):
		return '\n'.join([open(x).read() for x in files])
		