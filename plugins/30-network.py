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

		self.dlgEditIface = EditIfaceDialog()
		self.dlgEditIface.btnCancel.Handler = lambda t,e,d: self.Core.Switch.Switch(self.Panel)
		self.dlgEditIface.btnOK.Handler = self.HIfaceEdited
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
			self.dlgEditIface.lblTitle.Text = 'Interface options for ' + t.Iface
			self.dlgEditIface.IfaceName = t.Iface
			self.dlgEditIface.txtAddress.Text = self.Interfaces.Entries[t.Iface].Params['address']
			self.dlgEditIface.txtNetmask.Text = self.Interfaces.Entries[t.Iface].Params['netmask']
			self.dlgEditIface.txtGateway.Text = self.Interfaces.Entries[t.Iface].Params['gateway']
			self.dlgEditIface.txtDNS.Text = self.Interfaces.Entries[t.Iface].Params['dns-nameserver']
			self.dlgEditIface.txtPreUp.Text = self.Interfaces.Entries[t.Iface].Params['pre-up']
			self.dlgEditIface.txtPostUp.Text = self.Interfaces.Entries[t.Iface].Params['post-up']
			self.dlgEditIface.txtPreDown.Text = self.Interfaces.Entries[t.Iface].Params['pre-down']
			self.dlgEditIface.txtPostDown.Text = self.Interfaces.Entries[t.Iface].Params['post-down']
			self.dlgEditIface.txtNetwork.Text = self.Interfaces.Entries[t.Iface].Params['network']
			self.dlgEditIface.txtBroadcast.Text = self.Interfaces.Entries[t.Iface].Params['broadcast']
			self.dlgEditIface.txtMetric.Text = self.Interfaces.Entries[t.Iface].Params['metric']
			self.dlgEditIface.txtMTU.Text = self.Interfaces.Entries[t.Iface].Params['mtu']
			self.dlgEditIface.txtHwaddr.Text = self.Interfaces.Entries[t.Iface].Params['hwaddress']
		return

	def HIfaceEdited(self, t, e, d):
		self.Interfaces.Entries[self.dlgEditIface.IfaceName].Params['address'] = self.dlgEditIface.txtAddress.Text
		self.Interfaces.Entries[self.dlgEditIface.IfaceName].Params['netmask'] = self.dlgEditIface.txtNetmask.Text
		self.Interfaces.Entries[self.dlgEditIface.IfaceName].Params['gateway'] = self.dlgEditIface.txtGateway.Text
		self.Interfaces.Entries[self.dlgEditIface.IfaceName].Params['dns-nameserver'] = self.dlgEditIface.txtDNS.Text
		self.Interfaces.Entries[self.dlgEditIface.IfaceName].Params['pre-up'] = self.dlgEditIface.txtPreUp.Text
		self.Interfaces.Entries[self.dlgEditIface.IfaceName].Params['post-up'] = self.dlgEditIface.txtPostUp.Text
		self.Interfaces.Entries[self.dlgEditIface.IfaceName].Params['pre-down'] = self.dlgEditIface.txtPreDown.Text
		self.Interfaces.Entries[self.dlgEditIface.IfaceName].Params['post-down'] = self.dlgEditIface.txtPostDown.Text
		self.Interfaces.Entries[self.dlgEditIface.IfaceName].Params['network'] = self.dlgEditIface.txtNetwork.Text
		self.Interfaces.Entries[self.dlgEditIface.IfaceName].Params['broadcast'] = self.dlgEditIface.txtBroadcast.Text
		self.Interfaces.Entries[self.dlgEditIface.IfaceName].Params['metric'] = self.dlgEditIface.txtMetric.Text
		self.Interfaces.Entries[self.dlgEditIface.IfaceName].Params['mtu'] = self.dlgEditIface.txtMTU.Text
		self.Interfaces.Entries[self.dlgEditIface.IfaceName].Params['hwaddress'] = self.dlgEditIface.txtHwaddr.Text
		self.Interfaces.Save()
		self.Core.Switch.Switch(self.Panel)
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
						e.Params[a[0]] = ' '.join(a[1:])

				if (len(ss)>1): ss = ss[1:]
				else: ss = []
		return

	def Save(self):
		f = open('/etc/network/interfaces', 'w')
		for i in self.Entries.keys():
			self.Entries[i].Save(f)
		f.close()
		return


class InterfacesEntry:
	Name = ""
	Auto = True
	Class = ""
	Mode = ""
	Params = None

	def __init__(self):
		self.Params = { 'address':'', 'netmask':'', 'gateway':'', 'network':'', 'broadcast':'', 'dns-nameserver':'', 'metric':'', 'mtu':'', 'hwaddr':'', 'pre-up':'', 'pre-down':'', 'post-up':'', 'post-down':'', 'hwaddress':''}

	def Save(self, f):
		if self.Auto: f.write('auto ' + self.Name + '\n')
		f.write('iface ' + self.Name + ' ' + self.Class + ' ' + self.Mode + '\n')
		for k in self.Params.keys():
			if self.Params[k] != '':
				f.write('\t' + k + ' ' + self.Params[k] + '\n')
		f.write('\n')
		return

class EditIfaceDialog(ui.DialogBox):
	txtAddress = None
	txtNetmask = None
	txtGateway = None
	txtDNS = None
	txtPreUp = None
	txtPostUp = None
	txtPreDown = None
	txtPostDown = None
	txtNetwork = None
	txtBroadcast = None
	txtMetric = None
	txtMTU = None
	txtHwaddr = None

	def __init__(self):
		ui.DialogBox.__init__(self)
		self.lblTitle.Text = 'Edit interface options'
		t = ui.Table([], True)
		t.Widths = [150,200]
		self.Width = "auto"

		self.txtAddress = ui.Input()
		self.txtNetmask = ui.Input()
		self.txtGateway = ui.Input()
		self.txtDNS = ui.Input()
		self.txtPreUp = ui.Input()
		self.txtPreDown = ui.Input()
		self.txtPostUp = ui.Input()
		self.txtPostDown = ui.Input()
		self.txtNetwork = ui.Input()
		self.txtBroadcast = ui.Input()
		self.txtMetric = ui.Input()
		self.txtMTU = ui.Input()
		self.txtHwaddr = ui.Input()

		l = ui.Label('Basic')
		l.Size = 3
		t.Rows.append(ui.TableRow([l]))
		t.Rows.append(ui.TableRow([ui.Label('IP address:'), self.txtAddress], True))
		t.Rows.append(ui.TableRow([ui.Label('Netmask:'), self.txtNetmask], True))
		t.Rows.append(ui.TableRow([ui.Label('Gateway:'), self.txtGateway], True))

		t.Rows.append(ui.Spacer(1,30))

		l = ui.Label('Scripts')
		l.Size = 3
		t.Rows.append(ui.TableRow([l]))
		t.Rows.append(ui.TableRow([ui.Label('Pre-up:'), self.txtPreUp], True))
		t.Rows.append(ui.TableRow([ui.Label('Post-up:'), self.txtPostUp], True))
		t.Rows.append(ui.TableRow([ui.Label('Pre-down:'), self.txtPreDown], True))
		t.Rows.append(ui.TableRow([ui.Label('Post-down:'), self.txtPostDown], True))

		t.Rows.append(ui.Spacer(1,30))

		l = ui.Label('Advanced')
		l.Size = 3
		t.Rows.append(ui.TableRow([l]))
		t.Rows.append(ui.TableRow([ui.Label('Assigned DNS:'), self.txtDNS], True))
		t.Rows.append(ui.TableRow([ui.Label('Network:'), self.txtNetwork], True))
		t.Rows.append(ui.TableRow([ui.Label('Broadcast:'), self.txtBroadcast], True))
		t.Rows.append(ui.TableRow([ui.Label('Metric:'), self.txtMetric], True))
		t.Rows.append(ui.TableRow([ui.Label('MTU:'), self.txtMTU], True))
		t.Rows.append(ui.TableRow([ui.Label('Hardware address:'), self.txtHwaddr], True))

		self.Inner = t
		self.Visible = False

