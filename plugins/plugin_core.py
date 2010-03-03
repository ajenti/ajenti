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
	
	def OnLoad(self, s, u):
		self.UI = u
		self.Session = s

		mw = ui.MainWindow()

		self.TopBar = ui.TopBar()
		mw.AddElement(self.TopBar)

		b = ui.Action()
		b.Text="Asd"
		b.Icon = "ok"
		b.Description="Qwerty"

		l = ui.VContainer()
		l.AddElement(b)
		l.AddElement(b)
		l.AddElement(b)
		l.AddElement(b)

		mw.AddElement(l)
				
		b = ui.Button()
		mw.AddElement(b)
		b.Text="Asd"
		b.Handler = self.handler

		self.UI.Root = mw

		log.info('CorePlugin', 'Started instance')
		

	def OnHandleRequest():
		return

	def handler(self, t, e, d):
		t.Text += '.'

