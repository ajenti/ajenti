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
	platform = ['debian', 'ubuntu']

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
		self._edit_apache_modules.btnOK.tag = 'modules'
		self._edit_apache_modules.btnOK.handler = self.back_button_clicked

	def build_panel(self):
		l = ui.Label('Apache')
		l.size = 5
		self._lblStats = ui.Label()

		c = ui.HContainer([ui.Image('plug/apache;bigicon.png'), ui.Spacer(10,1), ui.VContainer([l, self._lblStats])])
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
		if st == 'w3m: Can\'t load http://localhost:80/server-status.':

			self._lblStats.text = 'Apache is currently down'
			self._actStratStop.text = 'Start'
			self._act_start_stop_description.text = 'Start Apache server'

			self._isRunning = 0
			return 0

		else:

			self._lblStats.text = 'Apache is working'
			self._actStratStop.text = 'Stop'
			self._act_start_stop_description.text = 'Stop Apache server'

			self._isRunning = 1
			return 1

	def InstallButtonClicked(self,t,e,d):
		print t, e, d
		#if t == self._actInstall:
		#	tools.actions['apache/install'].run()
		#if t == self._actRemove:
		#	tools.actions['apache/remove'].run()

		# Bad, bad code
		# This stuff won't work, 'cause you can't delete the panel
		# Consider updating it in self.update()
		this.Panel = None
		self.build_panel()
		return

	def StartStopBtnClicked(self,t,e,d):
		if t == self._actStratStop:
			if self._isRunning == 1:
				tools.actions['apache/status'].run('stop')
			else:
				tools.actions['apache/status'].run('start')
		return

	def menuClicked(self,t,e,d):
		if t.tag == 'modules':
			self.panel.visible = False
			self._edit_apache_modules.visible = True

		if t.tag == 'hosts':
			self.panel.visible = False
		return

	def back_button_clicked(self,t,e,d):
		if t.tag == 'modules':
			self.panel.visible = True
			self._edit_apache_modules.visible = False

		if t.tag == 'hosts':
			self.panel.visible = False
		return


class ApacheHosts():
	_avaible = None
	_enable = None

	def parse(self):
		self._avaible = {}
		self._enable = {}

		return
	def save(self):
		return


class ApacheModule():
	enabled = False
	name = ''
	description = ''
	hasConfig = False
	# Files
	config = ''
	load = ''

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


class EditApacheModulesDialog(ui.DialogBox):
	def __init__(self):
		ui.DialogBox.__init__(self)
		self.lblTitle.text = 'Apache Modules'

		self.width = "auto"
		self.visible = False

		self.btnOK.text = "Back"
		self.btnCancel.visible = False

		apm = ApacheModules()
		modules = apm.parse()

		t = ui.DataTable()
		r = ui.DataTableRow([ui.Label('Name'), ui.Label('Control')])
		t.widths = [150,200]
		r.is_header = True
		t.rows.append(r)

		for m in modules:

			description = ui.Label(m.description)

			name = None
			if m.hasConfig:
				name = ui.Link(m.name)
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
