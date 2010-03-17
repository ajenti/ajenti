from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import tools

class ServicesPluginMaster(PluginMaster):
	name = 'Services'

	def make_instance(self):
		i = ServicesPluginInstance(self)
		self.instances.append(i)
		return i


class ServicesPluginInstance(PluginInstance):
	name = 'Services'
	_lblStat = None
	svcs = None
	_tblSvcs = None

	def _on_load(self, s):
		PluginInstance._on_load(self, s)

		c = ui.Category()
		c.text = 'Services'
		c.description = 'Manage initscripts'
		c.icon = 'plug/services;icon'
		self.category_item = c
		self.svcs = Services()
		self.build_panel()
		log.info('ServicesPlugin', 'Started instance')


	def build_panel(self):
		self._lblStat = ui.Label()
		l = ui.Label('Services management')
		l.size = 5

		c = ui.HContainer([ui.Image('plug/services;bigicon.png'), ui.Spacer(10,1), ui.VContainer([l, self._lblStat])])
		self._tblSvcs = ui.DataTable()
		self._tblSvcs.title = 'Services'
		self._tblSvcs.widths = [200,100,100,100]
		r = ui.DataTableRow([ui.Label('Name'), ui.Label('Status'), ui.Label('PID'), ui.Label('Control')], True)
		r.is_header = True
		self._tblSvcs.rows.append(r)

		self.panel = ui.VContainer([c, ui.Spacer(1,10), self._tblSvcs])
		return

	def update(self):
		if self.panel.visible:
			self.svcs.rescan()
			self._tblSvcs.rows = [self._tblSvcs.rows[0]]
			cr = 0
			for e in self.svcs.list:
				l1 = ui.Link('Start')
				l1.tag = 'start'
				if e.status == 'start/running':
					cr += 1
					l1.text = 'Stop'
					l1.tag = 'stop'
				l1.svc = e.name
				l1.handler = self._on_service_clicked
				self._tblSvcs.rows.append(ui.DataTableRow([ui.Label(e.name), ui.Label(e.status), ui.Label(e.pid), ui.HContainer([l1])]))
			self._lblStat.text = str(cr) + ' running'
		return

	def _on_service_clicked(self, t, e, d):
		if t.tag == 'start':
			tools.actions['services/start'].run(t.svc)
		if t.tag == 'stop':
			tools.actions['services/stop'].run(t.svc)


class Services:
	list = None

	def rescan(self):
		ss = tools.actions['services/list'].run().splitlines()
		self.list = []

		for s in ss:
			a = s.split(' ')
			if a[1][0] == '(':
				a[0] += ' ' + a[1]
				a.remove(a[1])

			e = Service()
			e.name = a[0]
			self.list.append(e)
			e.status = a[1].strip(',')
			if e.status == 'start/running' and len(a)>3:
				e.pid = a[3]
		self.list.sort()


class Service:
	name = ''
	status = 'stop/waiting'
	pid = ''

	def __cmp__(self, other):
		if not self.status == other.status:
			return cmp(self.status, other.status)
		return cmp(self.name, other.name)


class ListAction(tools.Action):
	name = 'list'
	plugin = 'services'

	def run(self, d = ''):
		return tools.actions['core/shell-run'].run('initctl list')


class StartAction(tools.Action):
	name = 'start'
	plugin = 'services'

	def run(self, d = ''):
		return tools.actions['core/shell-run'].run('/etc/init.d/' + d + ' start')

class StopAction(tools.Action):
	name = 'stop'
	plugin = 'services'

	def run(self, d = ''):
		return tools.actions['core/shell-run'].run('/etc/init.d/' + d + ' stop')

class StatusAction(tools.Action):
	name = 'status'
	plugin = 'services'

	def run(self, d = ''):
		return tools.actions['core/shell-run'].run('initctl status ' + d)

class PureStatusAction(tools.Action):
	name = 'status-pure'
	plugin = 'services'

	def run(self, d = ''):
		return tools.actions['core/shell-run'].run('/etc/init.d/' + d + ' status')
