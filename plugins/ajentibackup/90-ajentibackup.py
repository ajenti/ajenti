from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import tools
import ajentibackup.core
import os
import subprocess
import time

class AjentiBackupPluginMaster(PluginMaster):
	name = 'Ajenti Backup'

	def make_instance(self):
		i = AjentiBackupPluginInstance(self)
		self.instances.append(i)
		return i


class AjentiBackupPluginInstance(PluginInstance):
	name = 'Ajenti Backup'
	_tbljobs = None
	_tblRuns = None
	_dlgEdit = None
	_btnAdd = None

	def _on_load(self, s):
		PluginInstance._on_load(self, s)

		c = ui.Category()
		c.text = 'Backup'
		c.description = 'Configure Ajenti backup'
		c.icon = 'plug/ajentibackup;icon'
		self.category_item = c
		self.build_panel()
		log.info('AjentiBackupPlugin', 'Started instance')

	def _on_post_load(self):
		self.session.register_panel(self._dlgEdit)

	def build_panel(self):
		self._lblUptime = ui.Label()
		l = ui.Label('Ajenti Backup')
		l.size = 5

		self._tblRuns = ui.DataTable()
		self._tblRuns.title = 'Running jobs'
		self._tblRuns.widths = [100, 100, 300, 100]
		r = ui.DataTableRow([ui.Label('job name'), ui.Label('PID'), ui.Label('Status'), ui.Label('Control')])
		r.is_header = True
		self._tblRuns.rows.append(r)

		self._tbljobs = ui.DataTable()
		self._tbljobs.title = 'Scheduled backup jobs'
		self._tbljobs.widths = [200, 200, 200]
		r = ui.DataTableRow([ui.Label('Job name'), ui.Label('Path'), ui.Label('Control')])
		r.is_header = True
		self._tbljobs.rows.append(r)

		d = ui.VContainer()
		d.add_element(self._tblRuns)
		d.add_element(ui.Spacer(1,30))
		d.add_element(self._tbljobs)
		self._btnAdd = ui.Button('Add new')
		self._btnAdd.handler = self._on_add_clicked
		d.add_element(self._btnAdd)

		c = ui.HContainer([ui.Image('plug/ajentibackup;bigicon.png'), ui.Spacer(10,1), ui.VContainer([l])])
		self.panel = ui.VContainer([c, d])

		self._dlgEdit = EditJobDialog()
		self._dlgEdit.btnCancel.handler = lambda t,e,d: self.core.switch.switch(self.panel)
		self._dlgEdit.btnOK.handler = self._on_job_edited
		return

	def update(self):
		if self.panel.visible:
			ajentibackup.core.init()

			self._tblRuns.rows = [self._tblRuns.rows[0]]

			try:
				s = os.listdir('/var/run/ajenti-backup/')
			except:
				s = []

			self._tblRuns.visible = False
			for l in s:
				if '.pid' in l:
					n = l.split('.')[0]
					l1 = ui.Link('Abort')
					l1.handler = self._on_kill_clicked
					l1.pid = commands.getstatusoutput('cat /var/run/ajenti-backup/' + l)[1]
					l1.job = n
					r = ui.DataTableRow([ui.Label(n), ui.Label(l1.pid), ui.Label(commands.getstatusoutput('cat /var/run/ajenti-backup/' + n + '.status')[1]), l1])
					self._tblRuns.visible = True
					self._tblRuns.rows.append(r)

			self._tbljobs.rows = [self._tbljobs.rows[0]]
			for k in ajentibackup.core.jobs:
				j = ajentibackup.core.jobs[k]
				l1 = ui.Link('Edit')
				l2 = ui.Link('Delete')
				l3 = ui.Link('Run')
				l1.handler = self._on_control_clicked
				l2.handler = self._on_control_clicked
				l3.handler = self._on_control_clicked
				l1.job = j
				l2.job = j
				l3.job = j
				l1.tag = 'edit'
				l2.tag = 'delete'
				l3.tag = 'run'

				r = ui.DataTableRow([ui.Label(j.name), ui.Label(j.path), ui.HContainer([l1, l2, l3])])
				self._tbljobs.rows.append(r)
			return

	def _on_kill_clicked(self, t, e, d):
		ajentibackup.core.Canceljob(t.job)

	def _on_add_clicked(self, t, e, d):
		x = ui.Element()
		x.job = ajentibackup.core.job()
		x.tag = 'edit'
		ajentibackup.core.jobs['new'] = x.job
		self._on_control_clicked(x, 'click', None)

	def _on_control_clicked(self, t, e, d):
		if t.tag == 'delete':
			ajentibackup.core.jobs.remove(t.job)
			ajentibackup.core.save()
		if t.tag == 'edit':
			self.panel.visible = False
			self._dlgEdit.visible = True
			self._dlgEdit.job = t.job

			self._dlgEdit.txtName.text = t.job.name
			self._dlgEdit.txtTime.text = t.job.time
			self._dlgEdit.txtPath.text = t.job.path
			self._dlgEdit.txtBefore.text = t.job.before
			self._dlgEdit.txtAfter.text = t.job.after
			self._dlgEdit.txtUser.text = t.job.user
			self._dlgEdit.txtTemp.text = t.job.temp
			self._dlgEdit.txtFile.text = t.job.file
			self._dlgEdit.txtSendTo.text = t.job.sendto
			self._dlgEdit.txtExclude.text = ':'.join(t.job.exclude)
			self._dlgEdit.rBTAR.checked = t.job.method == 'tar'
			self._dlgEdit.rBNone.checked = t.job.method == 'none'
			self._dlgEdit.rSCopy.checked = t.job.sendby == 'copy'
			self._dlgEdit.rSNone.checked = t.job.sendby == 'none'
		if t.tag == 'run':
			subprocess.Popen(['ajenti-backup', 'run', t.job.name])
			time.sleep(0.5)

	def _on_job_edited(self, t, e, d):
		j = self._dlgEdit.job
		d = self._dlgEdit
		j.name = d.txtName.text
		j.time = d.txtTime.text
		j.path = d.txtPath.text
		j.before = d.txtBefore.text
		j.after = d.txtAfter.text
		j.user = d.txtUser.text
		j.temp = d.txtTemp.text
		j.file = d.txtFile.text
		j.sendto = d.txtSendTo.text
		j.exclude = d.txtExclude.text.split(':')
		if d.rBTAR.checked: j.Method = 'tar'
		if d.rBNone.checked: j.Method = 'none'
		if d.rSCopy.checked: j.sendby = 'copy'
		if d.rSNone.checked: j.sendby = 'none'
		ajentibackup.core.save()
		self.core.switch.switch(self.panel)

		
class EditJobDialog(ui.DialogBox):
	txtPath = None
	txtBefore = None
	txtAfter = None
	txtExclude = None
	txtSendTo = None
	txtName = None
	txtTemp = None
	txtUser = None
	txtFile = None
	txtTime = None
	rBTAR = None
	rBNone = None
	rSCopy = None
	rSNone = None

	def __init__(self):
		ui.DialogBox.__init__(self)
		self.lblTitle.text = 'Edit backup job'
		t = ui.LayoutTable([])
		t.widths = [150,200]
		self.width = "auto"

		self.txtPath = ui.Input()
		self.txtBefore = ui.Input()
		self.txtAfter = ui.Input()
		self.txtExclude = ui.Input()
		self.txtSendTo = ui.Input()
		self.txtName = ui.Input()
		self.txtTemp = ui.Input()
		self.txtUser = ui.Input()
		self.txtFile = ui.Input()
		self.txtTime = ui.Input()

		rg = ui.RadioGroup()
		rg.add(' GZipped TAR directory')
		rg.add(' Disabled')
		self.rBTAR = rg.get_box(0)
		self.rBNone = rg.get_box(1)
		t.rows.append(ui.LayoutTableRow([ui.Label('Backup method')], 2))
		t.rows.append(ui.LayoutTableRow([rg], 2))

		rg = ui.RadioGroup()
		rg.add(' File copy')
		rg.add(' Disabled')
		self.rSCopy = rg.get_box(0)
		self.rSNone = rg.get_box(1)
		t.rows.append(ui.LayoutTableRow([ui.Label('Send backup')], 2))
		t.rows.append(ui.LayoutTableRow([rg], 2))

		t.rows.append(ui.LayoutTableRow([ui.Spacer(1,15)]))
		t.rows.append(ui.LayoutTableRow([ui.Label('job name:'), self.txtName]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Folder to backup:'), self.txtPath]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Send to:'), self.txtSendTo]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Schedule (cron format):'), self.txtTime]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Exclude:'), self.txtExclude]))
		t.rows.append(ui.LayoutTableRow([ui.Label('As user:'), self.txtUser]))
		t.rows.append(ui.LayoutTableRow([ui.Label('File name:'), self.txtFile]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Temporary folder:'), self.txtTemp]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Run script before:'), self.txtBefore]))
		t.rows.append(ui.LayoutTableRow([ui.Label('Run script after:'), self.txtAfter]))
		t.rows.append(ui.LayoutTableRow([ui.Spacer(1,30)]))

		self.inner = t
		self.visible = False
