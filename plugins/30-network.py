from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import sensors

class NetworkPluginMaster(PluginMaster):
	Name = 'Network'

	def OnLoad(self):
		PluginMaster.OnLoad(self)

	def MakeInstance(self):
		i = NetworkPluginInstance()
		self.Instances.append(i)
		return i


class NetworkPluginInstance(PluginInstance):
	UI = None
	Session = None
	Name = 'Network'
	Master = None
	_lblUptime = None
	_tblIfaces = None
	_tblIfacesW = [100,100,200,100,100,150]

	def OnLoad(self, s, u):
		self.UI = u
		self.Session = s

		c = ui.Category()
		c.Text = 'Network'
		c.Description = 'Configure adapters'
		c.Icon = 'plug/network;icon'
		self.CategoryItem = c

		self.BuildPanel()

		log.info('NetworkPlugin', 'Started instance')


	def BuildPanel(self):
#		self._lblUptime = ui.Label('&nbsp;Uptime: ' + sensors.Script('powermgmt','uptime'))
		l = ui.Label('Networking')
		l.Size = 5

		c = ui.HContainer([ui.Image('plug/network;bigicon.png'), ui.Spacer(10,1), ui.VContainer([l])])
		d = ui.VContainer([])

		t = ui.Table()
		r = ui.TableRow([ui.Label('Interface'), ui.Label('Mode'), ui.Label('Address'), ui.Label('Status'), ui.Label('Carrier'), ui.Label('Control')])
		r.Widths = self._tblIfacesW
		r.IsHeader = True
		t.Rows.append(r)
		self._tblIfaces = t

		d.AddElement(ui.Label('Network interfaces'))
		d.AddElement(t)
		self.Panel = ui.VContainer([c, ui.Spacer(1,10), d])
		return


	def Update(self):
		if self.Panel.Visible:
			self._tblIfaces.Rows = [self._tblIfaces.Rows[0]]
			ifs = sensors.Script('network', 'list')
			ifs = ifs.split('\n')
			for s in ifs:
				l1 = ui.Link('Edit')
				l2 = ui.Link('Bring down')
				r = ui.TableRow([ui.Label(s), ui.Label(''), ui.Label(''), ui.Label(''), ui.Label(''), ui.HContainer([l1, l2])])
				r.Widths = self._tblIfacesW
				self._tblIfaces.Rows.append(r)
		return

