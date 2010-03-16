from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import tools

class CorePluginMaster(PluginMaster):
	name = 'Core'

	def make_instance(self):
		i = CorePluginInstance(self)
		self.instances.append(i)
		return i


class CorePluginInstance(PluginInstance):
	name = 'Core'
	switch = None
	_topbar = None
	_categories = None

	def _on_load(self, s):
		PluginInstance._on_load(self, s)

		self._categories = []
		self._panels = []
		self.switch = ui.SwitchContainer()

		log.info('CorePlugin', 'Started instance')

	def _on_post_load(self):
		mw = ui.MainWindow()

		self._topbar = ui.TopBar()
		mw.add_element(self._topbar)

		l = ui.VContainer()
		r = self.switch

		for p in self.session.plugins:
			if p.category_item != None:
				l.add_element(p.category_item)
				self._categories.append(p.category_item)
				p.category_item.handler = self._on_category_clicked
			if p.panel != None:
				r.add_element(p.panel)
			p.core = self

		mw.add_element(l)
		mw.add_element(r)
		self.session.ui.root = mw
		self._on_category_clicked(self._categories[0], '', '')

	def _on_category_clicked(self, t, e, d):
		for c in self._categories:
			c.selected = False
		t.selected = True
		self.switch.switch(self.switch.elements[self._categories.index(t)])


class ScriptAction(tools.Action):
	name = 'script-run'
	plugin = 'core'

	def run(self, d):
		return commands.getstatusoutput('./plugins/' + d[0] + '/scripts/' + d[1] + ' ' + d[2])[1]


class ScriptStatusAction(tools.Action):
	name = 'script-status'
	plugin = 'core'

	def run(self, d):
		return commands.getstatusoutput('./plugins/' + d[0] + '/scripts/' + d[1] + ' ' + d[2])[0]


class ShellAction(tools.Action):
	name = 'shell-run'
	plugin = 'core'

	def run(self, d):
		return commands.getstatusoutput(d)[1]


class ShellStatusAction(tools.Action):
	name = 'shell-status'
	plugin = 'core'

	def run(self, d):
		return commands.getstatusoutput(d)[0]


class DetectDistroAction(tools.Action):
	name = 'detect-distro'
	plugin = 'core'

	def run(self, d=None):
		s, r = commands.getstatusoutput('lsb_release -sd')
		if s == 0: return r
		s, r = commands.getstatusoutput('uname -mrs')
		return r
		

