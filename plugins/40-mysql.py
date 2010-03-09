from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import tools

class MySQLPluginMaster(PluginMaster):
	Name = 'MySQL'

	def OnLoad(self):
		PluginMaster.OnLoad(self)

	def MakeInstance(self):
		i = PowerMgmtPluginInstance()
		self.Instances.append(i)
		return i


class PowerMgmtPluginInstance(PluginInstance):
	UI = None
	Session = None
	Name = 'MySQL'
	_lblUptime = None
	_btnStart = None
	_btnRestart = None

	def OnLoad(self, s, u):
		self.UI = u
		self.Session = s

		c = ui.Category()
		c.Text = 'MySQL'
		c.Description = 'Configure databases'
		c.Icon = 'plug/mysql;icon'
		self.CategoryItem = c

		self.BuildPanel()

		log.info('MySQLPlugin', 'Started instance')


	def BuildPanel(self):
		self._lblUptime = ui.Label()
		l = ui.Label('MySQL Server Control')
		l.Size = 5

		self._btnStart = ui.Button()
		self._btnStart.Text = 'Start'
		self._btnStart.Handler = self.HButtonClicked
		self._btnRestart = ui.Button()
		self._btnRestart.Text = 'Restart'
		self._btnRestart.Handler = self.HButtonClicked

		c = ui.HContainer([ui.Image('plug/mysql;bigicon.png'), ui.Spacer(10,1), ui.VContainer([l, self._lblUptime])])
		d = ui.HContainer([self._btnStart, self._btnRestart])
		self.Panel = ui.VContainer([c, d])
		return


	def HButtonClicked(self, t, e, d):
		if t == self._actReset:
			tools.Actions['powermgmt/reboot'].Run()
		return

	def Update(self):
		if self.Panel.Visible:
			self._btnStart.Text = tools.Actions['services/status'].Run('myqsl')
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
