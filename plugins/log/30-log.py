from plugin import PluginMaster, PluginInstance #Import base plugin classes from Ajenti's plugin.py
import commands
import session # Ajenti session controller
import ui # Ajenti WebUI
import log
import tools # Support for actions
import sys
import os


# Plugins themselves consist of two parts: Master plugin and Instance plugin
# The Master plugin is launched when Ajenti server starts
# The Instance plugins are launched one per user session

class LogPluginMaster(PluginMaster):
	name = 'Log'

	def _on_load(self): # This event is fired when Ajenti loads the plugin
		PluginMaster._on_load(self)

	def make_instance(self): # Should return a new Instance plugin
		i = LogPluginInstance(self)
		self.instances.append(i)
		return i


class LogPluginInstance(PluginInstance):
	# Standard properties
	name = 'Log'

	# Our custom stuff
	_pathLabel = None;
	_pathTree = None;	

	def _on_load(self, s): # The session controller instance is passed to this method
		PluginInstance._on_load(self, s)

		# Build a category switcher for Ajenti
		c = ui.Category()
		c.text = 'Log'
		c.description = '/var/log/ veiwer'
		c.icon = 'plug/log;icon' # This means that image is stored in plugins/beeper/icon.png
		self.category_item = c # The category_item property will be later examined by Core plugin. If it isn't None, the new Category will be added to the UI

		self.build_panel()	
	
		log.info('LogPlugin', 'Started instance') # Available methods are log.info, log.warn, log.err. The first parameter is 'sender' name, the second is string being logged

	def build_panel(self):
		# The Ajenti web UI has tree-like structure based on containers

		# Make a header
		l = ui.Label('Log demo plugin')
		l.size = 5

		# The top block
		c = ui.HContainer([ui.Image('plug/ajentibackup;bigicon.png'), ui.Spacer(10, 1), l])

		_pathLabel = ui.Label('/usr/log/')
		
		"""
		_pathTree = ui.TreeContainer()
		tn1 = ui.TreeContainerNode('logs')
		tn2 = ui.TreeContainerNode('apache')
		tn3 = ui.Label('access.log')
		tn4 = ui.Label('error.log')
		tn5 = ui.Label('kern.log')
		_pathTree.add_element(tn1)
		tn2.add_element(tn3)
		tn2.add_element(tn4)
		tn1.add_element(tn2)
		tn1.add_element(tn5)
		"""
		
		tv = TreeViewer()
		tv.view()
		
		s = ui.ScrollContainer([tv.get_TreeContainer()])
		s.width = 250
		s.height = 400
		
		ta = ui.TextArea('Hello text aread')
		ta.width = 700
		ta.height = 380		
				
		#ta = ui.ScrollContainer([log_text])
		#ta.width = 700
		#ta.height = 380
		
		v1 = ui.VContainer([_pathLabel, ta])
		c1 = ui.HContainer([s, ui.Spacer(10, 1), v1])
		

		# Assemble the stuff altogether
		self.panel = ui.VContainer([c, c1])
		return


	def update(self): # The method is fired when user requests an updated UI view
		return


class TreeViewer():
	_dirname = "/var/log/"
	_cTree = None
	
	
	def get_TreeContainer(self):
		return self._cTree
	
	
	def view(self):
		self._cTree = ui.TreeContainer()
		
		dirList = [d for d in os.listdir(self._dirname)
				if os.path.isdir(os.path.join(self._dirname, d))]
				
		tn = []
		i = 0
		
		for d in dirList:
			tn.append(ui.TreeContainerNode(d))
			
			try:
				fileList = [f for f in os.listdir(self._dirname+d+"/")
					if os.path.isfile(os.path.join(self._dirname+d+"/", f))]
				
				for fl in fileList:
					tn[i].add_element(ui.Link(fl))
					
			except: print 'Cannot view files in folder: '+self._dirname+d+"/"
				

				
			self._cTree.add_element(tn[i])			
			i=i+1
		return
	

