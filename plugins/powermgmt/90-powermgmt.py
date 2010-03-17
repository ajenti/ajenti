from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import tools

class PowerMgmtPluginMaster(PluginMaster):
	name = 'Power management'

	def make_instance(self):
		i = PowerMgmtPluginInstance(self)
		self.instances.append(i)
		return i


class PowerMgmtPluginInstance(PluginInstance):
	name = 'Power management'
	_lblUptime = None
	_actReset = None
	_actShutdown = None

	def _on_load(self, s):
		PluginInstance._on_load(self, s)

		c = ui.Category()
		c.text = 'Power'
		c.description = 'Reboot and shutdown'
		c.icon = 'plug/powermgmt;icon'
		self.category_item = c
		self.build_panel()
		log.info('PowerMgmtplugin', 'Started instance')

	def build_panel(self):
		self._lblUptime = ui.Label()
		l = ui.Label('Power management')
		l.size = 5

		self._actReset = ui.Action()
		self._actReset.text = 'Restart'
		self._actReset.description = 'Shutdown system and boot again'
		self._actReset.icon = 'plug/powermgmt;reset'
		self._actReset.handler = self._on_button_clicked
		self._actShutdown = ui.Action()
		self._actShutdown.text = 'Shutdown'
		self._actShutdown.description = 'Halt the system and switch off the power'
		self._actShutdown.icon = 'plug/powermgmt;shutdown'
		self._actShutdown.handler = self._on_button_clicked

		c = ui.HContainer([ui.Image('plug/powermgmt;bigicon.png'), ui.Spacer(10,1), ui.VContainer([l, self._lblUptime])])
		d = ui.HContainer([self._actReset, self._actShutdown])
		self.panel = ui.VContainer([c, d])
		return


	def _on_button_clicked(self, t, e, d):
		if t == self._actReset:
			tools.actions['powermgmt/reboot'].run()
		if t == self._actShutdown:
			tools.actions['powermgmt/shutdown'].run()
		return

	def Update(self):
		if self.panel.visible:
			self._lblUptime.text = '&nbsp;Uptime: ' + tools.actions['powermgmt/uptime-hms'].run()
		return


class UptimeAction(tools.Action):
	name = 'uptime'
	plugin = 'powermgmt'

	def run(self, d = None):
		return tools.actions['core/script-run'].run(['powermgmt', 'uptime', ''])

class UptimeHMSAction(tools.Action):
	name = 'uptime-hms'
	plugin = 'powermgmt'

	def run(self, d = None):
		s = int(tools.actions['core/script-run'].run(['powermgmt', 'uptime', '']))
		h = s / 3600
		m = s / 60 % 60
		s = s % 60
		return str(h) + ':' + str(m) + ':' + str(s)

class ShutdownAction(tools.Action):
	name = 'shutdown'
	plugin = 'powermgmt'

	def run(self, d = None):
		return tools.actions['core/script-run'].run(['powermgmt', 'shutdown', ''])

class RebootAction(tools.Action):
	name = 'reboot'
	plugin = 'powermgmt'

	def run(self, d = None):
		return tools.actions['core/script-run'].run(['powermgmt', 'reboot', ''])
