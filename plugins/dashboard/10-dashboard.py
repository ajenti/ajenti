from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import config
import tools

class DashboardPluginMaster(PluginMaster):
	Name = 'Dashboard'

	def OnLoad(self):
		PluginMaster.OnLoad(self)

	def MakeInstance(self):
		i = DashboardPluginInstance()
		self.Instances.append(i)
		return i


class DashboardPluginInstance(PluginInstance):
	UI = None
	Session = None
	Name = 'Dashboard'
	Master = None

	_lblServerName = None
	_lblAjentiVer = None
	_lblDistro = None

	def OnLoad(self, s, u):
		self.UI = u
		self.Session = s

		c = ui.Category()
		c.Text = 'Dashboard'
		c.Description = 'Server status'
		c.Icon = 'plug/dashboard;icon'
		self.CategoryItem = c

		self.BuildPanel()

		log.info('DashboardPlugin', 'Started instance')
		return

	def BuildPanel(self):
		self._lblServerName = ui.Label()
		self._lblAjentiVer = ui.Label()
		self._lblDistro = ui.Label()
		self._lblServerName.Size = 5

		c = ui.HContainer([ui.Image('plug/dashboard;server.png'), ui.Spacer(10,1), ui.VContainer([self._lblServerName, self._lblDistro, self._lblAjentiVer])])
		self.Panel = ui.Container([c])
		return

	def Update(self):
		self._lblServerName.Text = config.ServerName
		self._lblAjentiVer.Text = '&nbsp;Ajenti ' + config.AjentiVersion
		self._lblDistro.Text = '&nbsp;' + tools.Actions['core/detect-distro'].Run(None)
		return

