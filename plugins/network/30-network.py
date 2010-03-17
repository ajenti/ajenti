from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import tools

class NetworkPluginMaster(PluginMaster):
	name = 'Network'
	platform = 'any' #['debian', 'ubuntu']

	def make_instance(self):
		i = NetworkPluginInstance(self)
		self.instances.append(i)
		return i


class NetworkPluginInstance(PluginInstance):
	name = 'Network'
	_lblStats = None
	_tblifaces = None
	_tblDNS = None
	_btnAddDNS = None
	DNS = None
	interfaces = None
	dlgEditIface = None
	dlgEditDNS = None

	def _on_load(self, s):
		PluginInstance._on_load(self, s)

		c = ui.Category()
		c.text = 'Network'
		c.description = 'Configure adapters'
		c.icon = 'plug/network;icon'
		self.category_item = c

		self.build_panel()
		self.interfaces = InterfacesFile()
		self.DNS = DNSFile()
		log.info('NetworkPlugin', 'Started instance')

	def _on_post_load(self):
		self.session.register_panel(self.dlgEditIface)
		self.session.register_panel(self.dlgEditDNS)

	def build_panel(self):
		l = ui.Label('Networking')
		l.size = 5
		self._lblStats = ui.Label()

		c = ui.HContainer([ui.Image('plug/network;bigicon.png'), ui.Spacer(10,1), ui.VContainer([l, self._lblStats])])
		d = ui.VContainer([])

		t = ui.DataTable()
		t.title = 'Network interfaces'
		r = ui.DataTableRow([ui.Label('Interface'), ui.Label('mode'), ui.Label('Address'), ui.Label('Netmask'), ui.Label('Status'), ui.Label('Control')])
		t.widths = [100,100,100,100,100,200]
		r.is_header = True
		t.rows.append(r)
		self._tblifaces = t

		d.add_element(t)

		t = ui.DataTable()
		t.title = 'DNS nameservers'
		r = ui.DataTableRow([ui.Label('Element'), ui.Label('Value'), ui.Label('Control')])
		t.widths = [100,100,100]
		r.is_header = True
		t.rows.append(r)
		self._tblDNS = t

		d.add_element(ui.Spacer(1,20))
		d.add_element(t)
		self._btnAddDNS = ui.Button('Add new')
		self._btnAddDNS.handler = self._on_add_DNS_clicked
		d.add_element(self._btnAddDNS)

		self.panel = ui.VContainer([c, ui.Spacer(1,10), d])

		self.dlgEditIface = EditIfaceDialog()
		self.dlgEditIface.btnCancel.handler = lambda t,e,d: self.core.switch.switch(self.panel)
		self.dlgEditIface.btnOK.handler = self._on_iface_edited
		self.dlgEditDNS = EditDNSDialog()
		self.dlgEditDNS.btnCancel.handler = lambda t,e,d: self.core.switch.switch(self.panel)
		self.dlgEditDNS.btnOK.handler = self._on_DNS_edited
		return


	def update(self):
		if self.panel.visible:
			self.interfaces.parse()
			self._tblifaces.rows = [self._tblifaces.rows[0]]

			cup = 0

			for k in self.interfaces.entries.keys():
				s = self.interfaces.entries[k]
				st = tools.actions['network/ifstate'].run(s.name)
				a,m = tools.actions['network/ifaddr'].run(s.name)

				l1 = ui.Link('Edit')
				l2 = ui.Link('Bring down')
				l1.handler = self._on_iface_control_clicked
				l2.handler = self._on_iface_control_clicked
				l1.iface = s.name
				l2.iface = s.name
				l1.tag = 'edit'
				l2.tag = 'down'

				il = ui.ImageLabel('plug/network;if-' + st + '.png', 'Down')

				if st == 'up':
					il.text = 'Up'
					cup += 1
				else:
					l2.text = 'Bring up'
					l2.tag = 'up'
					a,m = ('','')

				r = ui.DataTableRow([ui.Label(s.name), ui.Label(s.mode), ui.Label(a), ui.Label(m), il, ui.HContainer([l1, l2])])

				self._tblifaces.rows.append(r)


			self.DNS.parse()
			self._tblDNS.rows = [self._tblDNS.rows[0]]
			i = 0
			for e in self.DNS.entries:
				l1 = ui.Link('Edit')
				l2 = ui.Link('Delete')
				l1.handler = self._on_DNS_control_clicked
				l2.handler = self._on_DNS_control_clicked
				l1.entry = i
				l2.entry = i
				l1.tag = 'edit'
				l2.tag = 'delete'
				i += 1
				r = ui.DataTableRow([ui.Label(e['element']), ui.Label(e['value']), ui.HContainer([l1, l2])])
				self._tblDNS.rows.append(r)

			self._lblStats.text = str(cup) + ' interfaces up out of ' + str(len(self.interfaces.entries)) + ' total'
		return


	def _on_iface_control_clicked(self, t, e, d):
		if t.tag == 'up':
			tools.actions['network/ifup'].run(t.iface)
		if t.tag == 'down':
			tools.actions['network/ifdown'].run(t.iface)
		if t.tag == 'edit':
			self.panel.visible = False
			self.dlgEditIface.visible = True
			self.dlgEditIface.lblTitle.text = 'Interface options for ' + t.iface
			self.dlgEditIface.ifaceName = t.iface
			self.dlgEditIface.txtAddress.text = self.interfaces.entries[t.iface].params['address']
			self.dlgEditIface.txtNetmask.text = self.interfaces.entries[t.iface].params['netmask']
			self.dlgEditIface.txtGateway.text = self.interfaces.entries[t.iface].params['gateway']
			self.dlgEditIface.txtDNS.text = self.interfaces.entries[t.iface].params['dns-nameserver']
			self.dlgEditIface.txtPreUp.text = self.interfaces.entries[t.iface].params['pre-up']
			self.dlgEditIface.txtPostUp.text = self.interfaces.entries[t.iface].params['post-up']
			self.dlgEditIface.txtPreDown.text = self.interfaces.entries[t.iface].params['pre-down']
			self.dlgEditIface.txtPostDown.text = self.interfaces.entries[t.iface].params['post-down']
			self.dlgEditIface.txtNetwork.text = self.interfaces.entries[t.iface].params['network']
			self.dlgEditIface.txtBroadcast.text = self.interfaces.entries[t.iface].params['broadcast']
			self.dlgEditIface.txtMetric.text = self.interfaces.entries[t.iface].params['metric']
			self.dlgEditIface.txtMTU.text = self.interfaces.entries[t.iface].params['mtu']
			self.dlgEditIface.txtHwaddr.text = self.interfaces.entries[t.iface].params['hwaddress']
			self.dlgEditIface.chkAuto.checked = self.interfaces.entries[t.iface].auto
			self.dlgEditIface.rLoopback.checked = self.interfaces.entries[t.iface].mode == 'loopback'
			self.dlgEditIface.rManual.checked = self.interfaces.entries[t.iface].mode == 'manual'
			self.dlgEditIface.rStatic.checked = self.interfaces.entries[t.iface].mode == 'static'
			self.dlgEditIface.rDHCP.checked = self.interfaces.entries[t.iface].mode == 'dhcp'
		return

	def _on_iface_edited(self, t, e, d):
		self.interfaces.entries[self.dlgEditIface.ifaceName].params['address'] = self.dlgEditIface.txtAddress.text
		self.interfaces.entries[self.dlgEditIface.ifaceName].params['netmask'] = self.dlgEditIface.txtNetmask.text
		self.interfaces.entries[self.dlgEditIface.ifaceName].params['gateway'] = self.dlgEditIface.txtGateway.text
		self.interfaces.entries[self.dlgEditIface.ifaceName].params['dns-nameserver'] = self.dlgEditIface.txtDNS.text
		self.interfaces.entries[self.dlgEditIface.ifaceName].params['pre-up'] = self.dlgEditIface.txtPreUp.text
		self.interfaces.entries[self.dlgEditIface.ifaceName].params['post-up'] = self.dlgEditIface.txtPostUp.text
		self.interfaces.entries[self.dlgEditIface.ifaceName].params['pre-down'] = self.dlgEditIface.txtPreDown.text
		self.interfaces.entries[self.dlgEditIface.ifaceName].params['post-down'] = self.dlgEditIface.txtPostDown.text
		self.interfaces.entries[self.dlgEditIface.ifaceName].params['network'] = self.dlgEditIface.txtNetwork.text
		self.interfaces.entries[self.dlgEditIface.ifaceName].params['broadcast'] = self.dlgEditIface.txtBroadcast.text
		self.interfaces.entries[self.dlgEditIface.ifaceName].params['metric'] = self.dlgEditIface.txtMetric.text
		self.interfaces.entries[self.dlgEditIface.ifaceName].params['mtu'] = self.dlgEditIface.txtMTU.text
		self.interfaces.entries[self.dlgEditIface.ifaceName].params['hwaddress'] = self.dlgEditIface.txtHwaddr.text
		self.interfaces.entries[self.dlgEditIface.ifaceName].auto = self.dlgEditIface.chkAuto.checked
		if self.dlgEditIface.rLoopback.checked: self.interfaces.entries[self.dlgEditIface.ifaceName].mode == 'loopback'
		if self.dlgEditIface.rStatic.checked: self.interfaces.entries[self.dlgEditIface.ifaceName].mode == 'static'
		if self.dlgEditIface.rManual.checked: self.interfaces.entries[self.dlgEditIface.ifaceName].mode == 'manual'
		if self.dlgEditIface.rDHCP.checked: self.interfaces.entries[self.dlgEditIface.ifaceName].mode == 'dhcp'
		self.interfaces.save()
		self.core.switch.switch(self.panel)
		return

	def _on_add_DNS_clicked(self, t, e, d):
		x = ui.Element()
		x.entry = len(self.DNS.entries)
		x.tag = 'edit'
		self.DNS.entries.append({'element':'nameserver', 'value':'0.0.0.0'})
		self._on_DNS_control_clicked(x, 'click', None)
		return

	def _on_DNS_control_clicked(self, t, e, d):
		if t.tag == 'delete':
			self.DNS.entries.remove(self.DNS.entries[t.entry])
			self.DNS.save()
		if t.tag == 'edit':
			self.panel.visible = False
			self.dlgEditDNS.visible = True
			self.dlgEditDNS.entry = t.entry
			self.dlgEditDNS.txtValue.text = self.DNS.entries[t.entry]['value']
			self.dlgEditDNS.rNS.checked = self.DNS.entries[t.entry]['element'] == 'nameserver'
			self.dlgEditDNS.rSearch.checked = self.DNS.entries[t.entry]['element'] == 'search'
			self.dlgEditDNS.rDomain.checked = self.DNS.entries[t.entry]['element'] == 'domain'
			self.dlgEditDNS.rOptions.checked = self.DNS.entries[t.entry]['element'] == 'options'
			return

	def _on_DNS_edited(self, t, e, d):
		self.DNS.entries[self.dlgEditDNS.entry]['value'] = self.dlgEditDNS.txtValue.text
		if self.dlgEditDNS.rNS.checked: self.DNS.entries[self.dlgEditDNS.entry]['element'] = 'nameserver'
		if self.dlgEditDNS.rSearch.checked: self.DNS.entries[self.dlgEditDNS.entry]['element'] = 'search'
		if self.dlgEditDNS.rDomain.checked: self.DNS.entries[self.dlgEditDNS.entry]['element'] = 'domain'
		if self.dlgEditDNS.rOptions.checked: self.DNS.entries[self.dlgEditDNS.entry]['element'] = 'options'
		self.DNS.save()
		self.core.switch.switch(self.panel)
		return


class InterfacesFile:
	entries = None

	def parse(self):
		self.entries = {}

		try:
			f = open('/etc/network/interfaces')
			ss = f.read().splitlines()
			f.close()
		except IOError, e:
			log.err('NetworkPlugin', str(e))
			return

		while len(ss)>0:
			if (len(ss[0]) > 0 and not ss[0][0] == '#'):
				a = ss[0].strip(' \t\n').split(' ')
				for s in a:
					if s == '': a.remove(s)
				if (a[0] == 'auto'):
					if not self.entries.has_key(a[1]):
						self.entries[a[1]] = InterfacesEntry()
					e = self.entries[a[1]]
					e.name = a[1]
					e.auto = True
				elif (a[0] == 'iface'):
					if not self.entries.has_key(a[1]):
						self.entries[a[1]] = InterfacesEntry()
					e = self.entries[a[1]]
					e.name = a[1]
					e.cls = a[2]
					e.mode = a[3]
				else:
					e.params[a[0]] = ' '.join(a[1:])
			if (len(ss)>1): ss = ss[1:]
			else: ss = []

	def save(self):
		f = open('/etc/network/interfaces', 'w')
		for i in self.entries.keys():
			self.entries[i].save(f)
		f.close()
		return


class InterfacesEntry:
	name = ""
	auto = True
	cls = ""
	mode = ""
	params = None

	def __init__(self):
		self.params = { 'address':'', 'netmask':'', 'gateway':'', 'network':'', 'broadcast':'', 'dns-nameserver':'', 'metric':'', 'mtu':'', 'hwaddr':'', 'pre-up':'', 'pre-down':'', 'post-up':'', 'post-down':'', 'hwaddress':''}

	def save(self, f):
		if self.auto:
			f.write('auto ' + self.name + '\n')
		f.write('iface ' + self.name + ' ' + self.cls + ' ' + self.mode + '\n')
		for k in self.params.keys():
			if self.params[k] != '':
				f.write('\t' + k + ' ' + self.params[k] + '\n')
		f.write('\n')


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
		self.lblTitle.text = 'Edit interface options'
		t = ui.LayoutTable([])
		t.widths = [150,200]
		self.width = "auto"

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
		l.size = 3
		t.rows.append(ui.LayoutTableRow([l]))
		t.rows.append(ui.LayoutTableRow([ui.Container([self.chkAuto, ui.Label(' Bring up automatically')])], 2))
		rg = ui.RadioGroup()
		rg.add(' Loopback')
		rg.add(' Static')
		rg.add(' Manual')
		rg.add(' DHCP')
		self.rLoopback = rg.get_box(0)
		self.rStatic = rg.get_box(1)
		self.rManual = rg.get_box(2)
		self.rDHCP = rg.get_box(3)
		t.rows.append(ui.LayoutTableRow([rg]))
		t.rows.append(ui.LayoutTableRow([ui.Spacer(1,15)]))

		l = ui.Label('Scripts')
		l.size = 3
		t.rows.append(ui.LayoutTableRow([l], True))
		t.rows.append(ui.LayoutTableRow([ui.Label('IP address:'), self.txtAddress]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Netmask:'), self.txtNetmask]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Gateway:'), self.txtGateway]))

		t.rows.append(ui.LayoutTableRow([ui.Spacer(1,15)]))

		l = ui.Label('Scripts')
		l.size = 3
		t.rows.append(ui.LayoutTableRow([l]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Pre-up:'), self.txtPreUp]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Post-up:'), self.txtPostUp]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Pre-down:'), self.txtPreDown]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Post-down:'), self.txtPostDown]))

		t.rows.append(ui.LayoutTableRow([ui.Spacer(1,15)]))

		l = ui.Label('Advanced')
		l.size = 3
		t.rows.append(ui.LayoutTableRow([l]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Assigned DNS:'), self.txtDNS]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Network:'), self.txtNetwork]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Broadcast:'), self.txtBroadcast]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Metric:'), self.txtMetric]))
		t.rows.append(ui.LayoutTableRow([ui.Label('MTU:'), self.txtMTU]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Hardware address:'), self.txtHwaddr]))

		t.rows.append(ui.LayoutTableRow([ui.Spacer(1,15)]))

		self.inner = t
		self.visible = False


class EditDNSDialog(ui.DialogBox):
	txtValue = None
	rNS = None
	rSearch = None
	rDomain = None
	rOptions = None

	def __init__(self):
		ui.DialogBox.__init__(self)
		self.lblTitle.text = 'Edit DNS list entry'
		t = ui.LayoutTable([])
		t.widths = [150,200]
		self.width = "auto"

		self.txtValue = ui.Input()

		rg = ui.RadioGroup()
		rg.add(' Nameserver')
		rg.add(' Search list')
		rg.add(' Local domain name')
		rg.add(' Option list')
		self.rNS = rg.get_box(0)
		self.rSearch = rg.get_box(1)
		self.rDomain = rg.get_box(2)
		self.rOptions = rg.get_box(3)
		t.rows.append(ui.LayoutTableRow([rg]))
		t.rows.append(ui.LayoutTableRow([ui.Spacer(1,15)]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Value:'), self.txtValue]))
		t.rows.append(ui.LayoutTableRow([ui.Spacer(1,15)]))

		self.inner = t
		self.visible = False


class DNSFile:
	entries = None

	def __init__(self):
		self.entries = []

	def parse(self):
		self.entries = []
		f = open('/etc/resolv.conf')
		ss = f.read().splitlines()
		f.close()

		while len(ss)>0:
			if (len(ss[0]) > 0 and not ss[0][0] == '#'):
				a = ss[0].strip(' \t\n').split(' ')
				for s in a:
					if s == '': a.remove(s)
				self.entries.append({'element': a[0], 'value':' '.join(a[1:])})
			if (len(ss)>1): ss = ss[1:]
			else: ss = []
		return

	def save(self):
		f = open('/etc/resolv.conf', 'w')
		for i in self.entries:
			f.write(i['element'] + ' ' + i['value'] + '\n')
		f.close()
		return


class IfdownAction(tools.Action):
	name = 'ifdown'
	plugin = 'network'

	def run(self, d = ''):
		return tools.actions['core/shell-run'].run('ifdown ' + d)

class IfupAction(tools.Action):
	name = 'ifup'
	plugin = 'network'

	def run(self, d = ''):
		return tools.actions['core/shell-run'].run('ifup ' + d)


class IfStateAction(tools.Action):
	name = 'ifstate'
	plugin = 'network'

	def run(self, d = ''):
		st = tools.actions['core/script-status'].run(['network', 'state', d])
		if st == 0: return 'up'
		return 'down'

class IfAddrAction(tools.Action):
	name = 'ifaddr'
	plugin = 'network'

	def run(self, d = ''):
		st = tools.actions['core/script-run'].run(['network', 'addr', d]).split(' ')
		a = '0.0.0.0'
		m = '255.0.0.0'
		for s in st:
			if s[0:4] == 'addr':
				a = s[5:]
			if s[0:4] == 'Mask':
				m = s[5:]
		return a, m
