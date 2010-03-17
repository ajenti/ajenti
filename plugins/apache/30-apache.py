import os
import glob
import re

from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import tools


class ApachePluginMaster(PluginMaster):
	name = 'Apache'
	platform = 'any' #['debian', 'ubuntu']

	def _on_load(self):
		PluginMaster._on_load(self)

	def make_instance(self):
		i = ApachePluginInstance(self)
		self.instances.append(i)
		return i


class ApachePluginInstance(PluginInstance):
	name = 'Apache'

	# #####
	# Apache status
	_isInstalled = 0
	_isRunning = 0
	_lblStats = None
	_lblAction = None

	# #####
	# Predifined buttons

	# Instal / Remove
	_install_remove_description = None
	_actInstallRemove = None
	# Start / Stop
	_act_start_stop_description = None
	_actStratStop = None

	# #####
	# Divs
	_main = None
	_main_tab = None

	# #####
	# Dialogs
	_edit_apache_modules = None
	_edit_apache_hosts = None


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
		# Apache modules dialog
		self.session.register_panel(self._edit_apache_modules)
		self._edit_apache_modules.session = self.session
		#Apache hosts
		self.session.register_panel(self._edit_apache_hosts)
		self._edit_apache_hosts.session = self.session
		

	def build_panel(self):
		l = ui.Label('Apache')
		l.size = 5
		self._lblStats = ui.Label()
		
		self._lblAction = ui.Link()

		c = ui.HContainer([
			ui.Image('plug/apache;bigicon.png'),
			ui.Spacer(10,1),
			ui.VContainer([
				l,
				ui.HContainer([
					self._lblStats,
					ui.Spacer(10,1),
					self._lblAction
				])
			])
		])
		
		d = ui.VContainer([])
		self._main = d

		# Creating components
		self.build_main_table()
		self.build_main_menu()

		self.add_install_remove_buttons() # This must be the last row

		self.build_start_stop_button()

		# Assemble the stuff altogether
		self.panel = ui.VContainer([c, d])

		# Creating dialogs
		self._edit_apache_modules = EditApacheModulesDialog()
		self._edit_apache_modules.parent = self
		self._edit_apache_hosts = EditApacheHostsDialog()
		self._edit_apache_hosts.parent = self

		return

	def build_main_table(self):
		t = ui.DataTable()
		r = ui.DataTableRow([ui.Label('Action'), ui.Label('Description')])
		t.widths = [100,400]
		r.is_header = True
		t.rows.append(r)

		self._main_tab = t
		self._main.add_element(t)

		return

	def build_main_menu(self):
		# Modules
		mod_btn = ui.Link('Modules')
		mod_btn.handler = self.menuClicked
		mod_btn.tag = 'modules'
		mod_row = ui.DataTableRow([mod_btn , ui.Label('Control Apache modules')])
		# Hosts
		host_btn = ui.Link('Hosts')
		host_btn.handler = self.menuClicked
		host_btn.tag = 'hosts'
		host_row = ui.DataTableRow([host_btn , ui.Label('Manage Apache virtual hosts')])

		# Appending rows to main table
		self._main_tab.rows.append( host_row )
		self._main_tab.rows.append( mod_row )


		return

	def build_start_stop_button(self):
		# Label
		self._act_start_stop_description = ui.Label()
		# Start / Stop button
		self._actStratStop = ui.Link()
		self._actStratStop.text = 'Start'
		self._actStratStop.handler = self.StartStopBtnClicked

		r = ui.DataTableRow([self._actStratStop , self._act_start_stop_description])
		self._main_tab.rows.append(r)

		return

	def add_install_remove_buttons(self):
		#Containers
		self._install_remove_description = ui.Label()

		#Remove button
		self._actInstallRemove = ui.Link()
		self._actInstallRemove.text = 'Install'
		self._actInstallRemove.handler = self.InstallButtonClicked

		#self._main.add_element( self._install_remove_btn )
		r = ui.DataTableRow([self._actInstallRemove , self._install_remove_description])
		self._main_tab.rows.append(r)
		return

	def update(self):
		if self.panel.visible:
			if self.FindApache():
				# Apache is installed
				self.isRunning()
				
			else:
				# Apache is not installed
				self._actStratStop.visible = False


	def FindApache(self):
		if os.path.exists('/etc/apache2'):
			self._isInstalled = 1
			log.info('ApachePlugin', 'Apache is installed')
			self._actInstallRemove.text = 'Remove'
			self._install_remove_description.text = 'Remove Apache server'
			return 1
		else:
			self._isInstalled = 0
			self._lblStats.text = 'Apache is not installed yet.'
			log.info('ApachePlugin', 'Apache is not installed.')
			self._actInstallRemove.text = 'Install'
			self._install_remove_description.text = 'Install Apache server'
			return 0

	def isRunning(self):
		st = tools.actions['apache/status'].run()
		#print st
		if st[:3] == 'w3m':

			self._lblStats.text = 'Apache is currently down'
			self._actStratStop.text = 'Start'
			self._act_start_stop_description.text = 'Start Apache server'
			
			self._isRunning = 0
			return 0

		else:

			self._lblStats.text = 'Apache is working'
			self._actStratStop.text = 'Stop'
			self._act_start_stop_description.text = 'Stop Apache server'
			
			self._lblAction.text = 'Restart'
			self._lblAction.handler = self.StartStopBtnClicked
			
			self._isRunning = 1
			return 1

	def InstallButtonClicked(self,t,e,d):
		if t == self._actInstall:
			tools.actions['apache/install'].run()
		if t == self._actRemove:
			tools.actions['apache/remove'].run()
		return
		
	def StartStopBtnClicked(self,t,e,d):
		if t == self._actStratStop:
			if self._isRunning == 1:
				tools.actions['apache/status'].run('stop')
			else:
				tools.actions['apache/status'].run('start')
		if t == self._lblAction:
			tools.actions['apache/status'].run('restart')
		return

	def menuClicked(self,t,e,d):
		if t.tag == 'modules':
			self.session.core.switch.switch(self._edit_apache_modules)

		if t.tag == 'hosts':
			self.session.core.switch.switch(self._edit_apache_hosts)
			
		return

class ApacheHost():
	enabled = False
	name = ''
	config = ''
	
	def __init__(self,name):
		self.name = name
		#Config
		f = open('/etc/apache2/sites-available/'+self.name, 'r')
		self.config = f.readlines()
		#Enabling
		if os.path.exists('/etc/apache2/sites-enabled/000-'+self.name):
			self.enabled = True
	
	def save(self):
		# Config
		c = open('/etc/apache2/sites-available/'+self.name,'w')
		for s in self.config:
			c.write(s)
		c.close()
		# Enable / Disable
		if self.enabled:
			os.symlink('/etc/apache2/sites-available/'+self.name,'/etc/apache2/sites-enabled/000-'+self.name)
		else:
			os.remove( '/etc/apache2/sites-enabled/000-'+self.name )
		
		# Restarting Apache
		tools.actions['apache/status'].run('restart')

		return
	
	def enable_disable_action(self,t,e,d):
		if self.enabled:
			self.enabled = False
			t.text = 'Enable'
		else:
			self.enabled = True
			t.text = 'Disable'
		self.save()
		return

class ApacheHosts():
	hosts = None
	
	def add(self, host):
		return
	
	def parse(self):
		self.hosts = []
		hosts = glob.glob('/etc/apache2/sites-available/*')
		for host in hosts:
			self.hosts.append( ApacheHost( host.replace('/etc/apache2/sites-available/','') ) )
		return self.hosts
	
	def saveAll(self):
		for m in self.hosts:
			m.save()
		return

class EditApacheHostConfig(ui.DialogBox):
	parent = None
	def __init__(self):
		ui.DialogBox.__init__(self)
		self.lblTitle.text = 'Apache Host configuration'
		self.width = "auto"
		self.visible = False
		
		
		ta = ui.TextArea( '' )
		ta.width = 600
		ta.height = 400
		
		parent = None
		
		self.btnCancel.handler = self.btn_clicked
		self.btnCancel.text = 'Back'
		self.btnOK.handler = self.btn_clicked
		self.btnOK.text = 'Save'
		
		self.inner = ta

	def customize(self, host):
		self.apache_host = ApacheHost(host)
		self.inner.text = ''.join(self.apache_host.config)

	def btn_clicked(self,t,e,d):
		if t == self.btnCancel:
			self.parent.session.core.switch.switch(self.parent)
		if t == self.btnOK:
			self.apache_host.config = self.inner.text
			self.apache_host.save()
		return

class EditApacheHostsDialog(ui.DialogBox):
	parent = None
	def __init__(self):
		ui.DialogBox.__init__(self)
		self.lblTitle.text = 'Apache Hosts'

		self.width = "auto"
		self.visible = False

		self.btnOK.text = "Back"
		self.btnOK.handler = self._on_back_clicked
		self.btnCancel.visible = False
		
		aph = ApacheHosts()
		hosts = aph.parse()

		t = ui.DataTable()
		r = ui.DataTableRow([ui.Label('Host'), ui.Label('Control')])
		t.widths = [150,200]
		r.is_header = True
		t.rows.append(r)

		for m in hosts:
			
			name = ui.Link(m.name)
			name.handler = self._on_module_clicked
			name.tag = m.name

			btn_enable_disable = ui.Link()
			btn_enable_disable.handler = m.enable_disable_action
			if m.enabled:
				btn_enable_disable.text = 'Disable'
			else:
				btn_enable_disable.text = 'Enable'


			f = ui.DataTableRow([ name, ui.HContainer([btn_enable_disable])])
			t.rows.append(f)

		self.inner = t
		self.tab = t
		
	def _on_back_clicked(self,t,e,d):
		if e == 'click' and t == self.btnOK:
			self.parent.session.core.switch.switch(self.parent.panel)

	def _on_module_clicked(self, t, e, d):
		if e == 'click':
			n = t.tag
			confd = EditApacheHostConfig()
			confd.customize(n)
			confd.parent = self
			self.session.register_panel(confd)
			self.session.core.switch.switch(confd)

class ApacheModule():
	enabled = False
	name = ''
	description = ''
	hasConfig = False
	# Files
	config = ''
	load = ''
	#Config dialog
	config_dialog = None

	def __init__(self,name):
		self.name = name
		self.enabled = False

		f = open('/etc/apache2/mods-available/'+self.name+'.load', 'r')
		self.load = f.readlines()

		if os.path.exists('/etc/apache2/mods-available/'+self.name+'.conf'):
			self.hasConfig = True
			f = open('/etc/apache2/mods-available/'+self.name+'.conf', 'r')
			self.config = f.readlines()

		if os.path.exists('/etc/apache2/mods-enabled/'+self.name+'.load'):
			self.enabled = True

	def save(self):
		# Writing config
		if self.hasConfig:
			c = open('/etc/apache2/mods-available/'+self.name+'.conf','w')
			for s in self.config:
				c.write(s)
			c.close()
		# Writing load script
		l = open('/etc/apache2/mods-available/'+self.name+'.load','w')
		for s in self.load:
			l.write(s)
		l.close()
		# Enable / Disable
		if self.enabled:
			os.symlink('/etc/apache2/mods-available/'+self.name+'.load','/etc/apache2/mods-enabled/'+self.name+'.load')
			if self.hasConfig:
				os.symlink('/etc/apache2/mods-available/'+self.name+'.conf','/etc/apache2/mods-enabled/'+self.name+'.conf')
		else:
			os.remove( '/etc/apache2/mods-enabled/'+self.name+'.load' )
			if self.hasConfig:
				os.remove( '/etc/apache2/mods-enabled/'+self.name+'.conf' )
		# Restarting Apache
		tools.actions['apache/status'].run('restart')
		return

	def enable_disable_action(self,t,e,d):
		if self.enabled:
			self.enabled = False
			t.text = 'Enable'
		else:
			self.enabled = True
			t.text = 'Disable'
		self.save()
		return
	
	'''
	def open_config_dialog(self,t,e,d):
		confd = EditApacheModuleConfig()
		self.session.switch.switch( confd )
		self.config_dialog = confd
		return
	'''

class ApacheModules():
	modules = None
	def parse(self):
		self.modules = []
		mods = glob.glob('/etc/apache2/mods-available/*.load')
		for mod in mods:
			self.modules.append( ApacheModule(mod.replace('/etc/apache2/mods-available/','').replace('.load','')) )
		return self.modules
	def saveAll(self):
		for m in self.modules:
			m.save()
		return

class EditApacheModuleConfig(ui.DialogBox):
	parent = None
	def __init__(self):
		ui.DialogBox.__init__(self)
		self.lblTitle.text = 'Apache Module configuration'
		self.width = "auto"
		self.visible = False
		
		
		ta = ui.TextArea( '' )
		ta.width = 600
		ta.height = 400
		
		parent = None
		
		self.btnCancel.handler = self.btn_clicked
		self.btnCancel.text = 'Back'
		self.btnOK.handler = self.btn_clicked
		self.btnOK.text = 'Save'
		
		self.inner = ta

	def customize(self, module):
		self.apache_module = ApacheModule(module)
		self.inner.text = ''.join(self.apache_module.config)

	def btn_clicked(self,t,e,d):
		if t == self.btnCancel:
			self.parent.session.core.switch.switch(self.parent)
		if t == self.btnOK:
			self.apache_module.config = self.inner.text
			self.apache_module.save()
		return

class EditApacheModulesDialog(ui.DialogBox):
	parent = None
	def __init__(self):
		ui.DialogBox.__init__(self)
		self.lblTitle.text = 'Apache Modules'

		self.width = "auto"
		self.visible = False

		self.btnOK.text = "Back"
		self.btnOK.handler = self._on_back_clicked
		self.btnCancel.visible = False
		
		apm = ApacheModules()
		modules = apm.parse()

		t = ui.DataTable()
		r = ui.DataTableRow([ui.Label('Name'), ui.Label('Control')])
		t.widths = [150,200]
		r.is_header = True
		t.rows.append(r)

		for m in modules:

			name = None
			if m.hasConfig:
				name = ui.Link(m.name)
				#name.handler = m.open_config_dialog
				name.handler = self._on_module_clicked
				name.tag = m.name
			else:
				name = ui.Label(m.name)

			btn_enable_disable = ui.Link()
			btn_enable_disable.handler = m.enable_disable_action
			if m.enabled:
				btn_enable_disable.text = 'Disable'
			else:
				btn_enable_disable.text = 'Enable'


			f = ui.DataTableRow([ name, ui.HContainer([btn_enable_disable])])
			t.rows.append(f)

		self.inner = t
		self.tab = t
		
	def _on_back_clicked(self,t,e,d):
		if e == 'click' and t == self.btnOK:
			self.parent.session.core.switch.switch(self.parent.panel)

	def _on_module_clicked(self, t, e, d):
		if e == 'click':
			n = t.tag
			confd = EditApacheModuleConfig()
			confd.customize(n)
			confd.parent = self
			self.session.register_panel(confd)
			self.session.core.switch.switch(confd)
			

class InstallAction(tools.Action):
	name = 'install'
	plugin = 'apache'

	def run(self, d = None):
		log.info('ApachePlugin','Starting install')
		out = tools.actions['core/script-run'].run(['apache', 'install', ''])
		log.info('ApachePlugin','Install complete')
		return out


class RemoveAction(tools.Action):
	name = 'remove'
	plugin = 'apache'

	def run(self, d = None):
		log.info('ApachePlugin','Starting removing')
		out = tools.actions['core/script-run'].run(['apache', 'remove', ''])
		log.info('ApachePlugin','Apache has been removed')
		return out


class StatusAction(tools.Action):
	name = 'status'
	plugin = 'apache'

	def run(self, d = ''):
		if d == '':
			out = tools.actions['core/script-run'].run(['apache', 'status', 'status'])
		else:
			out = tools.actions['core/script-run'].run(['apache', 'status', d])
		return out
