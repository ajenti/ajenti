from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import tools

class CorePluginMaster(PluginMaster):
	Name = 'Core'

	def OnLoad(self):
		PluginMaster.OnLoad(self)

	def MakeInstance(self):
		i = CorePluginInstance(self)
		self.Instances.append(i)
		return i


class CorePluginInstance(PluginInstance):
	TopBar = None
	Name = 'Core'
	_categories = None
	Switch = None

	def OnLoad(self, s):
		PluginInstance.OnLoad(self, s)

		self._categories = []
		self._panels = []
		r = ui.SwitchContainer()
		self.Switch = r

		log.info('CorePlugin', 'Started instance')


	def OnPostLoad(self):
		mw = ui.MainWindow()

		self.TopBar = ui.TopBar()
		mw.AddElement(self.TopBar)


		l = ui.VContainer()
		r = self.Switch

		for p in self.Session.Plugins:
			if not p.CategoryItem == None:
				l.AddElement(p.CategoryItem)
				self._categories.append(p.CategoryItem)
				p.CategoryItem.Handler = self.HCategoryClicked
			if not p.Panel == None:
				r.AddElement(p.Panel)
			p.Core = self

		mw.AddElement(l)
		mw.AddElement(r)

		self.Session.UI.Root = mw

		self.HCategoryClicked(self._categories[0], '', '')



	def Update(self):
		return


	def HCategoryClicked(self, t, e, d):
		for c in self._categories:
			c.Selected = False
		t.Selected = True
		self.Switch.Switch(self.Switch.Elements[self._categories.index(t)])


class ScriptAction(tools.Action):
	Name = 'script-run'
	Plugin = 'core'

	def Run(self, d):
		return commands.getstatusoutput('./plugins/' + d[0] + '/scripts/' + d[1] + ' ' + d[2])[1]

class ScriptStatusAction(tools.Action):
	Name = 'script-status'
	Plugin = 'core'

	def Run(self, d):
		return commands.getstatusoutput('./plugins/' + d[0] + '/scripts/' + d[1] + ' ' + d[2])[0]

class ShellAction(tools.Action):
	Name = 'shell-run'
	Plugin = 'core'

	def Run(self, d):
		return commands.getstatusoutput(d)[1]

class ShellStatusAction(tools.Action):
	Name = 'shell-status'
	Plugin = 'core'

	def Run(self, d):
		return commands.getstatusoutput(d)[0]

class DetectDistroAction(tools.Action):
	Name = 'detect-distro'
	Plugin = 'core'

	def Run(self, d):
		s, r = commands.getstatusoutput('lsb_release -sd')
		if s == 0: return r
		s, r = commands.getstatusoutput('uname -mrs')
		return r

class DetectPlatform(tools.Action):
	Name = 'detect-platform'
	Plugin = 'core'

	def Run(self, d = None):
		if tools.Actions['core/shell-status'].Run('cat /etc/issue | grep Fedora') == 0:
			return 'fedora'
		if tools.Actions['core/shell-status'].Run('cat /etc/issue | grep Ubuntu') == 0:
			return 'ubuntu'
		if tools.Actions['core/shell-status'].Run('test -e /etc/debian_version') == 0:
			return 'debian'
		return 'generic'