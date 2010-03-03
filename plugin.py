import os
import sys
 
Plugins = []
 
class PluginMaster(object):
	Name = 'undefined'
	Instances = []
	
	def OnLoad(self):
		self.Instances = []
 
	def MakeInstance(self):
		pass


class PluginInstance(object):
	Name = 'undefined'
 
	def OnLoad(self):
		pass
 
	def OnCommand(self, cmd, args):
		pass
 
 
def LoadPlugins():
	global Plugins
	
	ss = os.listdir('plugins') 
	sys.path.insert(0, 'plugins')
 
	for s in ss:
		print 'Found plugin', s
		__import__(os.path.splitext(s)[ 0], None, None, [''])

 
	for plugin in PluginMaster.__subclasses__():
		p = plugin()
		Plugins.append(p)
		p.OnLoad()


def Instantiate():
	global Plugins

	l = []
	for p in Plugins:
		l.append(p.MakeInstance())

	return l
