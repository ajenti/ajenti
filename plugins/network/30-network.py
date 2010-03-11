from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import tools
#import http

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
	_lblStats = None
	_tblIfaces = None
	_tblDNS = None
	_btnAddDNS = None
#	_btnRestartNetworking = None
	DNS = None
	Interfaces = None
	dlgEditIface = None
	dlgEditDNS = None

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
		self.DNS = DNSFile()
		log.info('NetworkPlugin', 'Started instance')

	def OnPostLoad(self):
		self.Core.Switch.AddElement(self.dlgEditIface)
		self.Core.Switch.AddElement(self.dlgEditDNS)


	def BuildPanel(self):
		l = ui.Label('Networking')
		l.Size = 5
		self._lblStats = ui.Label()

		c = ui.HContainer([ui.Image('plug/network;bigicon.png'), ui.Spacer(10,1), ui.VContainer([l, self._lblStats])])
		d = ui.VContainer([])

		t = ui.DataTable()
		t.Title = 'Network interfaces'
		r = ui.DataTableRow([ui.Label('Interface'), ui.Label('Mode'), ui.Label('Address'), ui.Label('Netmask'), ui.Label('Status'), ui.Label('Control')])
		t.Widths = [100,100,100,100,100,200]
		r.IsHeader = True
		t.Rows.append(r)
		self._tblIfaces = t

		d.AddElement(t)


		t = ui.DataTable()
		t.Title = 'DNS nameservers'
		r = ui.DataTableRow([ui.Label('Element'), ui.Label('Value'), ui.Label('Control')])
		t.Widths = [100,100,100]
		r.IsHeader = True
		t.Rows.append(r)
		self._tblDNS = t

		d.AddElement(ui.Spacer(1,20))
		d.AddElement(t)
		self._btnAddDNS = ui.Button('Add new')
		self._btnAddDNS.Handler = self.HAddDNSClicked
		d.AddElement(self._btnAddDNS)

		#self._btnRestartNetworking = ui.Action('Restart networking')
		#self._btnRestartNetworking.Icon = 'core;ui/icon-restart'
		#self._btnRestartNetworking.Description = 'Reconfigure adapters'
		#self._btnRestartNetworking.Handler = self.HRestartClicked
#		b = ui.HContainer([self._btnRestartNetworking])
		b = ui.HContainer()
		self.Panel = ui.VContainer([c, ui.Spacer(1,10), d, ui.Spacer(1,30), b])

		self.dlgEditIface = EditIfaceDialog()
		self.dlgEditIface.btnCancel.Handler = lambda t,e,d: self.Core.Switch.Switch(self.Panel)
		self.dlgEditIface.btnOK.Handler = self.HIfaceEdited
		self.dlgEditDNS = EditDNSDialog()
		self.dlgEditDNS.btnCancel.Handler = lambda t,e,d: self.Core.Switch.Switch(self.Panel)
		self.dlgEditDNS.btnOK.Handler = self.HDNSEdited
		return


	def Update(self):
		if self.Panel.Visible:
			self.Interfaces.Parse()
			self._tblIfaces.Rows = [self._tblIfaces.Rows[0]]

			cup = 0

			for k in self.Interfaces.Entries.keys():
				s = self.Interfaces.Entries[k]
				st = tools.Actions['network/ifstate'].Run(s.Name)
				a,m = tools.Actions['network/ifaddr'].Run(s.Name)

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

				r = ui.DataTableRow([ui.Label(s.Name), ui.Label(s.Mode), ui.Label(a), ui.Label(m), il, ui.HContainer([l1, l2])])

				self._tblIfaces.Rows.append(r)


			self.DNS.Parse()
			self._tblDNS.Rows = [self._tblDNS.Rows[0]]
			i = 0
			for e in self.DNS.Entries:
				l1 = ui.Link('Edit')
				l2 = ui.Link('Delete')
				l1.Handler = self.HDNSControlClicked
				l2.Handler = self.HDNSControlClicked
				l1.Entry = i
				l2.Entry = i
				l1.Tag = 'edit'
				l2.Tag = 'delete'
				i += 1
				r = ui.DataTableRow([ui.Label(e['element']), ui.Label(e['value']), ui.HContainer([l1, l2])])
				self._tblDNS.Rows.append(r)

			self._lblStats.Text = str(cup) + ' interfaces up out of ' + str(len(self.Interfaces.Entries)) + ' total'
		return


	def HIfaceControlClicked(self, t, e, d):
		if t.Tag == 'up':
			tools.Actions['network/ifup'].Run(t.Iface)
		if t.Tag == 'down':
			tools.Actions['network/ifdown'].Run(t.Iface)
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
			self.dlgEditIface.chkAuto.Checked = self.Interfaces.Entries[t.Iface].Auto
			self.dlgEditIface.rLoopback.Checked = self.Interfaces.Entries[t.Iface].Mode == 'loopback'
			self.dlgEditIface.rManual.Checked = self.Interfaces.Entries[t.Iface].Mode == 'manual'
			self.dlgEditIface.rStatic.Checked = self.Interfaces.Entries[t.Iface].Mode == 'static'
			self.dlgEditIface.rDHCP.Checked = self.Interfaces.Entries[t.Iface].Mode == 'dhcp'
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
		self.Interfaces.Entries[self.dlgEditIface.IfaceName].Auto = self.dlgEditIface.chkAuto.Checked
		if self.dlgEditIface.rLoopback.Checked: self.Interfaces.Entries[self.dlgEditIface.IfaceName].Mode == 'loopback'
		if self.dlgEditIface.rStatic.Checked: self.Interfaces.Entries[self.dlgEditIface.IfaceName].Mode == 'static'
		if self.dlgEditIface.rManual.Checked: self.Interfaces.Entries[self.dlgEditIface.IfaceName].Mode == 'manual'
		if self.dlgEditIface.rDHCP.Checked: self.Interfaces.Entries[self.dlgEditIface.IfaceName].Mode == 'dhcp'
		self.Interfaces.Save()
		self.Core.Switch.Switch(self.Panel)
		return

	def HAddDNSClicked(self, t, e, d):
		x = ui.Element()
		x.Entry = len(self.DNS.Entries)
		x.Tag = 'edit'
		self.DNS.Entries.append({'element':'nameserver', 'value':'0.0.0.0'})
		self.HDNSControlClicked(x, 'click', None)
		return

	def HDNSControlClicked(self, t, e, d):
		if t.Tag == 'delete':
			self.DNS.Entries.remove(self.DNS.Entries[t.Entry])
			self.DNS.Save()
		if t.Tag == 'edit':
			self.Panel.Visible = False
			self.dlgEditDNS.Visible = True
			self.dlgEditDNS.Entry = t.Entry
			self.dlgEditDNS.txtValue.Text = self.DNS.Entries[t.Entry]['value']
			self.dlgEditDNS.rNS.Checked = self.DNS.Entries[t.Entry]['element'] == 'nameserver'
			self.dlgEditDNS.rSearch.Checked = self.DNS.Entries[t.Entry]['element'] == 'search'
			self.dlgEditDNS.rDomain.Checked = self.DNS.Entries[t.Entry]['element'] == 'domain'
			self.dlgEditDNS.rOptions.Checked = self.DNS.Entries[t.Entry]['element'] == 'options'
			return

	def HDNSEdited(self, t, e, d):
		self.DNS.Entries[self.dlgEditDNS.Entry]['value'] = self.dlgEditDNS.txtValue.Text
		if self.dlgEditDNS.rNS.Checked: self.DNS.Entries[self.dlgEditDNS.Entry]['element'] = 'nameserver'
		if self.dlgEditDNS.rSearch.Checked: self.DNS.Entries[self.dlgEditDNS.Entry]['element'] = 'search'
		if self.dlgEditDNS.rDomain.Checked: self.DNS.Entries[self.dlgEditDNS.Entry]['element'] = 'domain'
		if self.dlgEditDNS.rOptions.Checked: self.DNS.Entries[self.dlgEditDNS.Entry]['element'] = 'options'
		self.DNS.Save()
		self.Core.Switch.Switch(self.Panel)
		return


	#def HRestartClicked(self, t, e, d):
	#	if e == 'click':
	#		sensors.Service('networking', 'restart')
	#		http.Restart()
	#	return


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
					a = ss[0].strip(' \t\n').split(' ')
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
	chkAuto = None
	rStatic = None
	rManual = None
	rLoopback = None
	rDHCP = None

	def __init__(self):
		ui.DialogBox.__init__(self)
		self.lblTitle.Text = 'Edit interface options'
		t = ui.LayoutTable([])
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
		self.chkAuto = ui.Checkbox()

		l = ui.Label('General')
		l.Size = 3
		t.Rows.append(ui.LayoutTableRow([l]))
		t.Rows.append(ui.LayoutTableRow([ui.Container([self.chkAuto, ui.Label(' Bring up automatically')])], 2))
		rg = ui.RadioGroup()
		rg.Add(' Loopback')
		rg.Add(' Static')
		rg.Add(' Manual')
		rg.Add(' DHCP')
		self.rLoopback = rg.GetBox(0)
		self.rStatic = rg.GetBox(1)
		self.rManual = rg.GetBox(2)
		self.rDHCP = rg.GetBox(3)
		t.Rows.append(ui.LayoutTableRow([rg]))
		t.Rows.append(ui.LayoutTableRow([ui.Spacer(1,30)]))

		l = ui.Label('Scripts')
		l.Size = 3
		t.Rows.append(ui.LayoutTableRow([l], True))
		t.Rows.append(ui.LayoutTableRow([ui.Label('IP address:'), self.txtAddress]))
		t.Rows.append(ui.LayoutTableRow([ui.Label('Netmask:'), self.txtNetmask]))
		t.Rows.append(ui.LayoutTableRow([ui.Label('Gateway:'), self.txtGateway]))

		t.Rows.append(ui.LayoutTableRow([ui.Spacer(1,30)]))

		l = ui.Label('Scripts')
		l.Size = 3
		t.Rows.append(ui.LayoutTableRow([l]))
		t.Rows.append(ui.LayoutTableRow([ui.Label('Pre-up:'), self.txtPreUp]))
		t.Rows.append(ui.LayoutTableRow([ui.Label('Post-up:'), self.txtPostUp]))
		t.Rows.append(ui.LayoutTableRow([ui.Label('Pre-down:'), self.txtPreDown]))
		t.Rows.append(ui.LayoutTableRow([ui.Label('Post-down:'), self.txtPostDown]))

		t.Rows.append(ui.LayoutTableRow([ui.Spacer(1,30)]))

		l = ui.Label('Advanced')
		l.Size = 3
		t.Rows.append(ui.LayoutTableRow([l]))
		t.Rows.append(ui.LayoutTableRow([ui.Label('Assigned DNS:'), self.txtDNS]))
		t.Rows.append(ui.LayoutTableRow([ui.Label('Network:'), self.txtNetwork]))
		t.Rows.append(ui.LayoutTableRow([ui.Label('Broadcast:'), self.txtBroadcast]))
		t.Rows.append(ui.LayoutTableRow([ui.Label('Metric:'), self.txtMetric]))
		t.Rows.append(ui.LayoutTableRow([ui.Label('MTU:'), self.txtMTU]))
		t.Rows.append(ui.LayoutTableRow([ui.Label('Hardware address:'), self.txtHwaddr]))

		self.Inner = t
		self.Visible = False


class EditDNSDialog(ui.DialogBox):
	txtValue = None
	rNS = None
	rSearch = None
	rDomain = None
	rOptions = None

	def __init__(self):
		ui.DialogBox.__init__(self)
		self.lblTitle.Text = 'Edit DNS list entry'
		t = ui.LayoutTable([])
		t.Widths = [150,200]
		self.Width = "auto"

		self.txtValue = ui.Input()

		rg = ui.RadioGroup()
		rg.Add(' Nameserver')
		rg.Add(' Search list')
		rg.Add(' Local domain name')
		rg.Add(' Option list')
		self.rNS = rg.GetBox(0)
		self.rSearch = rg.GetBox(1)
		self.rDomain = rg.GetBox(2)
		self.rOptions = rg.GetBox(3)
		t.Rows.append(ui.LayoutTableRow([rg]))
		t.Rows.append(ui.LayoutTableRow([ui.Spacer(1,15)]))
		t.Rows.append(ui.LayoutTableRow([ui.Label('Value:'), self.txtValue]))
		t.Rows.append(ui.LayoutTableRow([ui.Spacer(1,30)]))

		self.Inner = t
		self.Visible = False


class DNSFile:
	Entries = None

	def __init__(self):
		self.Entries = []

	def Parse(self):
		self.Entries = []
		f = open('/etc/resolv.conf')
		ss = f.read().splitlines()
		f.close()

		while len(ss)>0:
			if (len(ss[0]) > 0 and not ss[0][0] == '#'):
				a = ss[0].strip(' \t\n').split(' ')
				for s in a:
					if s == '': a.remove(s)
				self.Entries.append({'element': a[0], 'value':' '.join(a[1:])})
			if (len(ss)>1): ss = ss[1:]
			else: ss = []
		return

	def Save(self):
		f = open('/etc/resolv.conf', 'w')
		for i in self.Entries:
			f.write(i['element'] + ' ' + i['value'] + '\n')
		f.close()
		return



class IfdownAction(tools.Action):
	Name = 'ifdown'
	Plugin = 'network'

	def Run(self, d = ''):
		return tools.Actions['core/shell-run'].Run('ifdown ' + d)

class IfupAction(tools.Action):
	Name = 'ifup'
	Plugin = 'network'

	def Run(self, d = ''):
		return tools.Actions['core/shell-run'].Run('ifup ' + d)


class IfStateAction(tools.Action):
	Name = 'ifstate'
	Plugin = 'network'

	def Run(self, d = ''):
		st = tools.Actions['core/script-status'].Run(['network', 'state', d])
		if st == 0: return 'up'
		return 'down'

class IfAddrAction(tools.Action):
	Name = 'ifaddr'
	Plugin = 'network'

	def Run(self, d = ''):
		st = tools.Actions['core/script-run'].Run(['network', 'addr', d]).split(' ')
		a = '0.0.0.0'
		m = '255.0.0.0'
		for s in st:
			if s[0:4] == 'addr':
				a = s[5:]
			if s[0:4] == 'Mask':
				m = s[5:]
		return a, m
