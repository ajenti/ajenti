from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import tools

class PowerMgmtPluginMaster(PluginMaster):
	Name = 'Power management'

	def OnLoad(self):
		PluginMaster.OnLoad(self)

	def MakeInstance(self):
		i = PowerMgmtPluginInstance()
		self.Instances.append(i)
		return i


class PowerMgmtPluginInstance(PluginInstance):
	UI = None
	Session = None
	Name = 'Power management'
	_lblUptime = None
	_actReset = None
	_actShutdown = None

	def OnLoad(self, s, u):
		self.UI = u
		self.Session = s

		c = ui.Category()
		c.Text = 'Power'
		c.Description = 'Reboot and shutdown'
		c.Icon = 'plug/powermgmt;icon'
		self.CategoryItem = c

		self.BuildPanel()

		log.info('PowerMgmtPlugin', 'Started instance')


	def BuildPanel(self):
		self._lblUptime = ui.Label()
		l = ui.Label('Power management')
		l.Size = 5

		self._actReset = ui.Action()
		self._actReset.Text = 'Restart'
		self._actReset.Description = 'Shutdown system and boot again'
		self._actReset.Icon = 'plug/powermgmt;reset'
		self._actReset.Handler = self.HButtonClicked
		self._actShutdown = ui.Action()
		self._actShutdown.Text = 'Shutdown'
		self._actShutdown.Description = 'Halt the system and switch off the power'
		self._actShutdown.Icon = 'plug/powermgmt;shutdown'
		self._actShutdown.Handler = self.HButtonClicked

		c = ui.HContainer([ui.Image('plug/powermgmt;bigicon.png'), ui.Spacer(10,1), ui.VContainer([l, self._lblUptime])])
		d = ui.HContainer([self._actReset, self._actShutdown])
		self.Panel = ui.VContainer([c, d])
		return


	def HButtonClicked(self, t, e, d):
		if t == self._actReset:
			tools.Actions['powermgmt/reboot'].Run()
		if t == self._actShutdown:
			tools.Actions['powermgmt/shutdown'].Run()
		return

	def Update(self):
		if self.Panel.Visible:
			self._lblUptime.Text = '&nbsp;Uptime: ' + tools.Actions['powermgmt/uptime-hms'].Run()
		return


class UptimeAction(tools.Action):
	Name = 'uptime'
	Plugin = 'powermgmt'

	def Run(self, d = None):
		return tools.Actions['core/script-run'].Run(['powermgmt', 'uptime', ''])

class UptimeHMSAction(tools.Action):
	Name = 'uptime-hms'
	Plugin = 'powermgmt'

	def Run(self, d = None):
		s = int(tools.Actions['core/script-run'].Run(['powermgmt', 'uptime', '']))
		h = s / 3600
		m = s / 60 % 60
		s = s % 60
		return str(h) + ':' + str(m) + ':' + str(s)

class ShutdownAction(tools.Action):
	Name = 'shutdown'
	Plugin = 'powermgmt'

	def Run(self, d = None):
		return tools.Actions['core/script-run'].Run(['powermgmt', 'shutdown', ''])

class RebootAction(tools.Action):
	Name = 'reboot'
	Plugin = 'powermgmt'

	def Run(self, d = None):
		return tools.Actions['core/script-run'].Run(['powermgmt', 'reboot', ''])
