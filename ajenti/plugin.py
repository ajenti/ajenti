import os
import sys
import log
import tools
import glob


plugins = []

class PluginMaster(object):
	name = 'undefined'
	instances = []
	platform = ['any']

	def _on_load(self):
		self.instances = []

	def make_instance(self):
		pass

	def destroy(self):
		pass

		
class PluginInstance(object):
	name = 'undefined'
	category_item = None
	panel = None
	core = None
	master = None
	session = None

	def __init__(self, m):
		self.master = m

	def _on_load(self, sess):
		self.session = sess

 	def _on_post_load(self):
		pass

	def update(self):
		pass

	def destroy(self):
		pass

def load_all():
	global plugins

	sys.path.insert(0, 'plugins')
	ss = [os.path.basename(s) for s in glob.glob('plugins/*.py')]
 	ss.sort()

	for s in ss:
		__import__(os.path.splitext(s)[0], None, None, [''])
		log.info('Plugins', 'Found plugin ' + s)

	for plugin in PluginMaster.__subclasses__():
		p = plugin()
		plugins.append(p)
		p._on_load()
		
	for a in tools.Action.__subclasses__():
		tools.register_action(a())

def instantiate():
	global plugins

	l = []
	for p in plugins:
		l.append(p.make_instance())

	return l

def unload_all():
	global plugins

	for p in plugins:
		p.destroy()
