import os
import sys
import log
import tools

Plugins = []

class PluginMaster(object):
	Name = 'undefined'
	Instances = []
	Platforms = ['any']

	def OnLoad(self):
		self.Instances = []

	def MakeInstance(self):
		pass


class PluginInstance(object):
	Name = 'undefined'
	CategoryItem = None
	Panel = None
	Core = None
	Master = None
	Session = None

	def __init__(self, m):
		self.Master = m

	def OnLoad(self, sess):
		self.Session = sess

 	def OnPostLoad(self):
		pass

	def Update(self):
		pass


def LoadPlugins():
	global Plugins

	ss = os.listdir('plugins')
	sys.path.insert(0, 'plugins')
 	ss.sort()

	for s in ss:
		if '.py' in s:
			__import__(os.path.splitext(s)[0], None, None, [''])
			log.info('Plugins', 'Found plugin ' + s)

	for plugin in PluginMaster.__subclasses__():
		p = plugin()
		Plugins.append(p)
		p.OnLoad()
	for action in tools.Action.__subclasses__():
		tools.RegisterAction(action())

def Instantiate():
	global Plugins

	l = []
	for p in Plugins:
		l.append(p.MakeInstance())

	return l
