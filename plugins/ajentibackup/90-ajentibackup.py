from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import tools
import ajentibackup.core

class AjentiBackupPluginMaster(PluginMaster):
	Name = 'Ajenti Backup'

	def OnLoad(self):
		PluginMaster.OnLoad(self)

	def MakeInstance(self):
		i = AjentiBackupPluginInstance()
		self.Instances.append(i)
		return i


class AjentiBackupPluginInstance(PluginInstance):
	UI = None
	Session = None
	Name = 'Ajenti Backup'
	_tblJobs = None
	_dlgEdit = None
	_btnAdd = None
	
	def OnLoad(self, s, u):
		self.UI = u
		self.Session = s

		c = ui.Category()
		c.Text = 'Backup'
		c.Description = 'Configure Ajenti backup'
		c.Icon = 'plug/ajentibackup;icon'
		self.CategoryItem = c

		self.BuildPanel()

		log.info('AjentiBackupPlugin', 'Started instance')

	def OnPostLoad(self):
		self.Core.Switch.AddElement(self._dlgEdit)
	
	def BuildPanel(self):
		self._lblUptime = ui.Label()
		l = ui.Label('Ajenti Backup')
		l.Size = 5

		self._tblJobs = ui.Table()
		self._tblJobs.Widths = [200, 200, 200]
		r = ui.TableRow([ui.Label('Job name'), ui.Label('Path'), ui.Label('Control')])
		r.IsHeader = True
		self._tblJobs.Rows.append(r)
		
		d = ui.VContainer()
		d.AddElement(ui.Label('Scheduled backup jobs'))
		d.AddElement(self._tblJobs)
		self._btnAdd = ui.Button('Add new')
		self._btnAdd.Handler = self.HAddClicked
		d.AddElement(self._btnAdd)
		
		c = ui.HContainer([ui.Image('plug/ajentibackup;bigicon.png'), ui.Spacer(10,1), ui.VContainer([l])])
		self.Panel = ui.VContainer([c, d])
		
		self._dlgEdit = EditJobDialog()
		self._dlgEdit.btnCancel.Handler = lambda t,e,d: self.Core.Switch.Switch(self.Panel)
		self._dlgEdit.btnOK.Handler = self.HJobEdited
		return


	def HButtonClicked(self, t, e, d):
		if t == self._actReset:
			tools.Actions['powermgmt/reboot'].Run()
		if t == self._actShutdown:
			tools.Actions['powermgmt/shutdown'].Run()
		return

	def Update(self):
		if self.Panel.Visible:
			ajentibackup.core.Init()
			self._tblJobs.Rows = [self._tblJobs.Rows[0]]
			for k in ajentibackup.core.Jobs:
				j = ajentibackup.core.Jobs[k]
				l1 = ui.Link('Edit')
				l2 = ui.Link('Delete')
				l1.Handler = self.HControlClicked
				l2.Handler = self.HControlClicked
				l1.Job = j
				l2.Job = j
				l1.Tag = 'edit'
				l2.Tag = 'delete'
				
				r = ui.TableRow([ui.Label(j.Name), ui.Label(j.Path), ui.HContainer([l1, l2])])
				self._tblJobs.Rows.append(r)
			return


	def HAddClicked(self, t, e, d):
		x = ui.Element()
		x.Job = ajentibackup.core.Job()
		x.Tag = 'edit'
		ajentibackup.core.Jobs['new'] = x.Job
		self.HControlClicked(x, 'click', None)
		
	def HControlClicked(self, t, e, d):
		if t.Tag == 'delete':
			ajentibackup.core.Jobs.remove(t.Job)
			ajentibackup.core.Save()
		if t.Tag == 'edit':
			self.Panel.Visible = False
			self._dlgEdit.Visible = True
			self._dlgEdit.Job = t.Job
			
			self._dlgEdit.txtName.Text = t.Job.Name
			self._dlgEdit.txtTime.Text = t.Job.Time
			self._dlgEdit.txtPath.Text = t.Job.Path
			self._dlgEdit.txtBefore.Text = t.Job.Before
			self._dlgEdit.txtAfter.Text = t.Job.After
			self._dlgEdit.txtUser.Text = t.Job.User
			self._dlgEdit.txtTemp.Text = t.Job.Temp
			self._dlgEdit.txtFile.Text = t.Job.File
			self._dlgEdit.txtSendTo.Text = t.Job.SendTo
			self._dlgEdit.txtExclude.Text = ':'.join(t.Job.Exclude)
			self._dlgEdit.rBTAR.Checked = t.Job.Method == 'tar'
			self._dlgEdit.rBNone.Checked = t.Job.Method == 'none'
			self._dlgEdit.rSCopy.Checked = t.Job.SendBy == 'copy'
			self._dlgEdit.rSNone.Checked = t.Job.SendBy == 'none'
			
			return
	
	def HJobEdited(self, t, e, d):
		j = self._dlgEdit.Job
		d = self._dlgEdit
		j.Name = d.txtName.Text
		j.Time = d.txtTime.Text
		j.Path = d.txtPath.Text
		j.Before = d.txtBefore.Text
		j.After = d.txtAfter.Text
		j.User = d.txtUser.Text
		j.Temp = d.txtTemp.Text
		j.File = d.txtFile.Text
		j.SendTo = d.txtSendTo.Text
		j.Exclude = d.txtExclude.Text.split(':')
		if d.rBTAR.Checked: j.Method = 'tar'
		if d.rBNone.Checked: j.Method = 'none'
		if d.rSCopy.Checked: j.SendBy = 'copy'
		if d.rSNone.Checked: j.SendBy = 'none'
		ajentibackup.core.Save()
		self.Core.Switch.Switch(self.Panel)
		
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
		self.lblTitle.Text = 'Edit backup job'
		t = ui.Table([], True)
		t.Widths = [150,200]
		self.Width = "auto"

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
		rg.Add(' GZipped TAR directory')
		rg.Add(' Disabled')
		self.rBTAR = rg.GetBox(0)
		self.rBNone = rg.GetBox(1)
		t.Rows.append(ui.TableRow([ui.Label('Backup method')], True, True))
		t.Rows.append(ui.TableRow([rg], True, True))
		
		rg = ui.RadioGroup()
		rg.Add(' File copy')
		rg.Add(' Disabled')
		self.rSCopy = rg.GetBox(0)
		self.rSNone = rg.GetBox(1)
		t.Rows.append(ui.TableRow([ui.Label('Send backup')], True, True))
		t.Rows.append(ui.TableRow([rg], True, True))
		
		t.Rows.append(ui.TableRow([ui.Spacer(1,15)]))
		t.Rows.append(ui.TableRow([ui.Label('Job name:'), self.txtName], True))
		t.Rows.append(ui.TableRow([ui.Label('Backup what:'), self.txtPath], True))
		t.Rows.append(ui.TableRow([ui.Label('Send to:'), self.txtSendTo], True))
		t.Rows.append(ui.TableRow([ui.Label('When (cron format):'), self.txtTime], True))
		t.Rows.append(ui.TableRow([ui.Label('Exclude:'), self.txtExclude], True))
		t.Rows.append(ui.TableRow([ui.Label('As user:'), self.txtUser], True))
		t.Rows.append(ui.TableRow([ui.Label('File name:'), self.txtFile], True))
		t.Rows.append(ui.TableRow([ui.Label('Temp dir:'), self.txtTemp], True))
		t.Rows.append(ui.TableRow([ui.Label('Run before:'), self.txtBefore], True))
		t.Rows.append(ui.TableRow([ui.Label('Run after:'), self.txtAfter], True))
		t.Rows.append(ui.TableRow([ui.Spacer(1,30)]))

		self.Inner = t
		self.Visible = False
