import os

from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import tools


class ApachePluginMaster(PluginMaster):
	name = 'Apache'
	platform = ['debian', 'ubuntu']
	
	def _on_load(self):
		PluginMaster._on_load(self)

	def make_instance(self):
		i = ApachePluginInstance(self)
		self.instances.append(i)
		return i

		
class ApachePluginInstance(PluginInstance):
	name = 'Apache'
	
	# Apache status
	_isInstalled = 0
	_lblStats = None
	
	# Predifined buttons
	_actInstall = None
	_actRemove = None
	
	# Divs
	_main = None
	
	#Dialogs
	_EditApachePlugins = None
	
	def _on_load(self, s):
		PluginInstance._on_load(self, s)

		c = ui.Category()
		c.text = 'Apache'
		c.description = 'Configure httpd'
		c.icon = 'plug/apache;icon'
		self.category_item = c
				
		self.build_panel()
		log.info('ApachePlugin', 'Started instance')
		
	
	def _on_post_load(self):
		self.session.register_panel(self._EditApachePlugins)
		
	def build_panel(self):
		l = ui.Label('Apache')
		l.size = 5
		self._lblStats = ui.Label()

		c = ui.HContainer([ui.Image('plug/apache;bigicon.png'), ui.Spacer(10,1), ui.VContainer([l, self._lblStats])])
		d = ui.VContainer([])
		self._main = d
		
		self.addInstallRemoveButtons()
		
		# Assemble the stuff altogether
		self.panel = ui.VContainer([c, d])
		
		# Creating dialogs
		self._EditApachePlugins = EditApachePluginsDialog()
		
		return
		
	def addInstallRemoveButtons(self):
		#Remove button
		self._actRemove = ui.Button()
		self._actRemove.text = 'Remove'
		self._actRemove.description = 'Uninstall Apache server'
		self._actRemove.icon = 'plug/apache;icon'
		self._actRemove.Handler = self.InstallButtonClicked
		self._main.add_element(self._actRemove)
		#Install button
		self._actInstall = ui.Button()
		self._actInstall.text = 'Install'
		self._actInstall.description = 'Install Apache server'
		self._actInstall.icon = 'plug/apache;icon'
		self._actInstall.Handler = self.InstallButtonClicked
		self._main.add_element(self._actInstall)
		return
		
	def update(self):
		if self.panel.visible:
			if self.FindApache():
				self._lblStats.text = 'I can\'t believe it!'
				self._actInstall.visible = False
				self._actRemove.visible = True		
			else:
				self._actInstall.visible = True
				self._actRemove.visible = False
		
	def FindApache(self):
		if os.path.exists('/etc/apache2'):
			self._usInstalled = 1
			log.info('ApachePlugin', 'Apache is installed')
			return 1
		else:
			self._usInstalled = 0
			self._lblStats.text = 'Apache is not installed yet.'
			log.info('ApachePlugin', 'Apache is not installed.')
			return 0
			
	def ApacheStatus(self):
		return 0
			
	def InstallButtonClicked(self,t,e,d):
		if t == self._actInstall:
			tools.actions['apache/install'].run()
		if t == self._actRemove:
			tools.actions['apache/remove'].run()
		return
		
class EditApachePluginsDialog(ui.DialogBox):
	def __init__(self):
		ui.DialogBox.__init__(self)
		self.lblTitle.text = 'Apache plugins'
		self.Width = "auto"

class InstallAction(tools.Action):
	Name = 'install'
	Plugin = 'apache'
	
	def Run(self, d = None):
		log.info('ApachePlugin','Starting install')
		out = tools.Actions['core/script-run'].Run(['apache', 'install', ''])
		log.info('ApachePlugin','Install complete')
		return out
		
class RemoveAction(tools.Action):
	Name = 'remove'
	Plugin = 'apache'
	
	def Run(self, d = None):
		log.info('ApachePlugin','Starting removing')
		out = tools.Actions['core/script-run'].Run(['apache', 'remove', ''])
		log.info('ApachePlugin','Apache has been removed')
		return out
