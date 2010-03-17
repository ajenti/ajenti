import commands

from plugin import PluginMaster, PluginInstance
import session
import ui
import log
import config
import tools


class DashboardPluginMaster(PluginMaster):
	name = 'Dashboard'

	def make_instance(self):
		i = DashboardPluginInstance(self)
		self.instances.append(i)
		return i


class DashboardPluginInstance(PluginInstance):
	name = 'Dashboard'

	_lblServerName = None
	_lblAjentiVer = None
	_lblDistro = None

	def _on_load(self, s):
		PluginInstance._on_load(self, s)

		c = ui.Category()
		c.text = 'Dashboard'
		c.description = 'Server status'
		c.icon = 'plug/dashboard;icon'
		self.category_item = c

		self.build_panel()

		log.info('DashboardPlugin', 'Started instance')
		return

	def build_panel(self):
		self._lblServerName = ui.Label()
		self._lblAjentiVer = ui.Label()
		self._lblDistro = ui.Label()
		self._lblServerName.size = 5

		c = ui.HContainer([ui.Image('plug/dashboard;server.png'), ui.Spacer(10,1), ui.VContainer([self._lblServerName, self._lblDistro, self._lblAjentiVer])])
		self.panel = ui.Container([c])
		return

	def update(self):
		self._lblServerName.text = config.server_name
		self._lblAjentiVer.text = '&nbsp;Ajenti ' + config.ajenti_version
		self._lblDistro.text = '&nbsp;' + tools.actions['core/detect-distro'].run()
		return

