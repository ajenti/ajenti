from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log

class CorePluginMaster(PluginMaster):
	Name = 'Core'

	def OnLoad(self):
		PluginMaster.OnLoad(self)

	def MakeInstance(self):
		i = CorePluginInstance()
		self.Instances.append(i)
		return i


class CorePluginInstance(PluginInstance):
	UI = None
	Session = None
	TopBar = None
	Name = 'Core'
	Master = None
	_categories = None
	Switch = None

	def OnLoad(self, s, u):
		self.UI = u
		self.Session = s
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
			if not p.Dialogs == None:
				self.UI.Dialogs.AddElement(p.Dialogs)
			p.Core = self

		mw.AddElement(l)
		mw.AddElement(r)

		self.UI.Root = mw

		self.HCategoryClicked(self._categories[0], '', '')



	def Update(self):
		return


	def HCategoryClicked(self, t, e, d):
		for c in self._categories:
			c.Selected = False
		t.Selected = True
		self.Switch.Switch(self.Switch.Elements[self._categories.index(t)])


