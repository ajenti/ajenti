from plugin import PluginMaster, PluginInstance
import commands
import session
import ui 
import log
import tools
import sys
import os


class LogPluginMaster(PluginMaster):
	name = 'Log'

	def make_instance(self):
		i = LogPluginInstance(self)
		self.instances.append(i)
		return i


class LogPluginInstance(PluginInstance):
	name = 'Log'

	_pathLabel = None;
	_pathTree = None;
	_logArea = None	

	def _on_load(self, s): 
		PluginInstance._on_load(self, s)

		c = ui.Category()
		c.text = 'Log'
		c.description = '/var/log/ viewer'
		c.icon = 'plug/log;icon'
		self.category_item = c 

		self.build_panel()	
	
		log.info('LogPlugin', 'Started instance') 

	def build_panel(self):
		l = ui.Label('')
		l.size = 5

		c = ui.HContainer([ui.Image('plug/ajentibackup;bigicon.png'), ui.Spacer(10, 1), l])

		_pathLabel = ui.Label('/var/log/')
		
		lb = ui.Label('')
		self._logArea = lb
		sl = ui.ScrollContainer([lb])
		sl.width = 500
		sl.height = 380
		
		t = ui.TreeContainer()
		t.add_element(LogTreeNode('/var/log', self))
		t.elements[0].expanded = True
		
		s = ui.ScrollContainer([t])
		s.width = 180
		s.height = 400	
		
		v1 = ui.VContainer([_pathLabel, sl])
		c1 = ui.HContainer([s, ui.Spacer(10, 1), v1])
		self.panel = ui.VContainer([c, c1])

	def update(self):
		if self.panel.visible:
			return
	

class LogTreeNode(ui.TreeContainerNode):
	dir_name = ''
	owner = None
	
	def __init__(self, d='/var/log', own = None):
		ui.TreeContainerNode.__init__(self)
		print d
		self.text = os.path.basename(d)
		self.dir_name = d		
		self.owner = own
		self.rescan()
		
	def rescan(self):
		dirList = os.listdir(self.dir_name)
		dirList.sort()

		for x in dirList:
			try:
				if os.path.isdir(os.path.join(self.dir_name, x)):
					tn = LogTreeNode(os.path.join(self.dir_name, x), self.owner)
					self.add_element(tn)
				else:		
					tn = ui.Link(x)		
					tn.path = os.path.join(self.dir_name, x)
					tn.handler = self._on_link_clicked
					self.add_element(ui.TreeContainerSimpleNode(tn))
			except:
				pass	
	
	def _on_link_clicked(self, t, e, d):
		self.owner._logArea.text = "hello from log tree"	

