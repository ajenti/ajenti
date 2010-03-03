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
	_panels = None
		
	def OnLoad(self, s, u):
		self.UI = u
		self.Session = s
		log.info('CorePlugin', 'Started instance')
		

	def OnPostLoad(self):
		mw = ui.MainWindow()

		self.TopBar = ui.TopBar()
		mw.AddElement(self.TopBar)


		self._categories = []
		self._panels = []
		l = ui.VContainer()
		r = ui.VContainer()
	
		for p in self.Session.Plugins:
			if not p.CategoryItem == None:
				l.AddElement(p.CategoryItem)
				self._categories.append(p.CategoryItem)
				p.CategoryItem.Handler = self.HCategoryClicked
			if not p.Panel == None:
				r.AddElement(p.Panel)
				p.Panel.Visible = False
				self._panels.append(p.Panel)
#				p.CategoryItem.Handler = self.HCategoryClicked
				
		mw.AddElement(l)
		mw.AddElement(r)

		self.UI.Root = mw

		self.HCategoryClicked(self._categories[0], '', '')
		

	
	def OnHandleRequest():
		return


	def HCategoryClicked(self, t, e, d):
		for c in self._categories:
			c.Selected = False
		t.Selected = True
		for c in self._panels:
			c.Visible = False
		self._panels[self._categories.index(t)].Visible = True
		
		
	def handler(self, t, e, d):
		t.Text += '.'

