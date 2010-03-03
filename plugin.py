import os
import sys
import log
 
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
	CategoryItem = None
	Panel = None
	
	def OnLoad(self):
		pass
 
	def OnCommand(self, cmd, args):
		pass
 
 	def OnPostLoad(self):
		pass
		
 
def LoadPlugins():
	global Plugins
	
	ss = os.listdir('plugins') 
	sys.path.insert(0, 'plugins')
 	ss.sort()
 	
	for s in ss:
		try:
			__import__(os.path.splitext(s)[0], None, None, [''])
			log.info('Plugins', 'Found plugin ' + s)
		except:
			pass

 
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
