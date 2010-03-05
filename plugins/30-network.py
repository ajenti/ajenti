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
	_lblStats = None
	_tblIfaces = None
	Interfaces = None
	dlgEditIface = None

	def OnLoad(self, s, u):
		self.UI = u
		self.Session = s

		c = ui.Category()
		c.Text = 'Network'
		c.Description = 'Configure adapters'
		c.Icon = 'plug/network;icon'
		self.CategoryItem = c

		self.BuildPanel()
		self.Interfaces = InterfacesFile()
		log.info('NetworkPlugin', 'Started instance')

	def OnPostLoad(self):
		self.Core.Switch.AddElement(self.dlgEditIface)


	def BuildPanel(self):
		l = ui.Label('Networking')
		l.Size = 5
		self._lblStats = ui.Label()

		c = ui.HContainer([ui.Image('plug/network;bigicon.png'), ui.Spacer(10,1), ui.VContainer([l, self._lblStats])])
		d = ui.VContainer([])

		t = ui.Table()
		r = ui.TableRow([ui.Label('Interface'), ui.Label('Mode'), ui.Label('Address'), ui.Label('Netmask'), ui.Label('Status'), ui.Label('Control')])
		t.Widths = [100,100,100,100,100,200]
		r.IsHeader = True
		t.Rows.append(r)
		self._tblIfaces = t

		d.AddElement(ui.Label('Network interfaces'))
		d.AddElement(t)
		self.Panel = ui.VContainer([c, ui.Spacer(1,10), d])

		self.dlgEditIface = ui.DialogBox()
		self.dlgEditIface.lblTitle.Text = 'Edit interface options'
		t = ui.Table([], True)
		t.Widths = [200,300]
		t.Rows.append(ui.TableRow([ui.Label('IP address:'), ui.Input('...')], True))
		t.Rows.append(ui.TableRow([ui.Label('Netmask:'), ui.Input('...')], True))
		t.Rows.append(ui.TableRow([ui.Label('Gateway:'), ui.Input('...')], True))
		t.Rows.append(ui.TableRow([ui.Label('DNS:'), ui.Input('...')], True))
		self.dlgEditIface.Inner = t
		self.dlgEditIface.Visible = False
		return


	def Update(self):
		if self.Panel.Visible:
			self.Interfaces.Parse()
			self._tblIfaces.Rows = [self._tblIfaces.Rows[0]]

			cup = 0

			for k in self.Interfaces.Entries.keys():
				s = self.Interfaces.Entries[k]
				st = self._GetIfState(s.Name)
				a,m = self._GetIfAddr(s.Name)

				l1 = ui.Link('Edit')
				l2 = ui.Link('Bring down')
				l1.Handler = self.HIfaceControlClicked
				l2.Handler = self.HIfaceControlClicked
				l1.Iface = s.Name
				l2.Iface = s.Name
				l1.Tag = 'edit'
				l2.Tag = 'down'

				il = ui.ImageLabel('plug/network;if-' + st + '.png', 'Down')

				if st == 'up':
					il.Text = 'Up'
					cup += 1
				else:
					l2.Text = 'Bring up'
					l2.Tag = 'up'
					a,m = ('','')

				r = ui.TableRow([ui.Label(s.Name), ui.Label(s.Mode), ui.Label(a), ui.Label(m), il, ui.HContainer([l1, l2])])

				self._tblIfaces.Rows.append(r)

			self._lblStats.Text = str(cup) + ' interfaces up out of ' + str(len(self.Interfaces.Entries)) + ' total'
		return


	def _GetIfState(self, i):
		st = sensors.ScriptStatus('network', 'state', i)
		if st == 0: return 'up'
		return 'down'

	def _GetIfAddr(self, i):
		st = sensors.Script('network', 'addr', i).split(' ')
		a = '0.0.0.0'
		m = '255.0.0.0'
		for s in st:
			if s[0:4] == 'addr':
				a = s[5:]
			if s[0:4] == 'Mask':
				m = s[5:]
		return a, m

	def HIfaceControlClicked(self, t, e, d):
		if t.Tag == 'up':
			print sensors.Shell('sudo ifup ' + t.Iface)
		if t.Tag == 'down':
			sensors.Shell('sudo ifdown ' + t.Iface)
		if t.Tag == 'edit':
			self.Panel.Visible = False
			self.dlgEditIface.Visible = True

		return

class InterfacesFile:
	Entries = None

	def __init__(self):
		self.Entries = {}
		return

	def Parse(self):
		self.Entries = {}

		f = open('/etc/network/interfaces')
		ss = f.read().splitlines()
		f.close()

		while len(ss)>0:
			while len(ss)>0:
				if (len(ss[0]) > 0 and not ss[0][0] == '#'):
					a = ss[0].split(' ')
					for s in a:
						if s == '': a.remove(s)
					if (a[0] == 'auto'):
						if not self.Entries.has_key(a[1]):
							self.Entries[a[1]] = InterfacesEntry()
						e = self.Entries[a[1]]
						e.Name = a[1]
						e.Auto = True
					elif (a[0] == 'iface'):
						if not self.Entries.has_key(a[1]):
							self.Entries[a[1]] = InterfacesEntry()
						e = self.Entries[a[1]]
						e.Name = a[1]
						e.Class = a[2]
						e.Mode = a[3]
					else:
						e.Params[a[0]] = a[1:].join(' ')

				if (len(ss)>1): ss = ss[1:]
				else: ss = []
		return


class InterfacesEntry:
	Name = ""
	Auto = True
	Class = ""
	Mode = ""
	Params = None

	def __init__(self):
		self.Params = {}
