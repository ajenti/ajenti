import random
import util

class UI:

	Root = None
	UpdatedElement = None
	Dialogs = None

	def __init__(self):
		self.Dialogs = Container()
		return

	def DumpBasePage(self):
		s = ''#<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">';
		s += '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ru">'
		s += '<head><meta http-equiv="content-type" content="text/html; charset=utf-8" />'
		s += '<title>Ajenti alpha</title>'
		s += '<link href="/dl;core;ui.css" rel="stylesheet" media="all" />'
		s += '<link rel="shortcut icon" href="/dl;core;ui/favicon.png" />'
		s += '<script src="/dl;core;ajax.js"></script></head>\n<body id="main">'
#		s += '<script src="/dl;core;loadpage.js"></script>'
		s += self.DumpHTML()
		s += "</body></html>"
		return s


	def DumpHTML(self):
		return self.Root.DumpHTML() + self.Dialogs.DumpHTML()



class Element(object):
	Visible = True
	ID = ''
	Handler = None
	Disabled = False

	def __init__(self):
		self.ID = str(random.randint(1, 9000*9000))

	def DumpHTML(self):
		return ''

	def Handle(self, target, event, data):
		if self.ID == target and not self.Handler == None:
			self.Handler(self, event, data)


class Container(Element):
	Elements = []

	def __init__(self, e=[]):
		Element.__init__(self)
		self.Elements = []
		self.Elements += e
		return

	def Clear(self):
		self.Elements = []
		return

	def AddElement(self, e):
		self.Elements.append(e)
		return

	def RemoveElement(self, e):
		self.Elements.remove(e)
		return

	def Handle(self, target, event, data):
		Element.Handle(self, target, event, data)
		for e in self.Elements:
			if e.Visible:
				e.Handle(target, event, data)

	def DumpHTML(self):
		s = ''
		if self.Visible:
			for e in self.Elements:
				s += e.DumpHTML()

		return s


class HContainer(Container):
	def __init__(self, e=[]):
		Container.__init__(self)
		self.Elements = []
		self.Elements += e
		return

	def DumpHTML(self):
		s = ''
		if self.Visible:
			s += '<table cellspacing="0" cellpadding="0"><tr>'
			for e in self.Elements:
				s += '<td>' + e.DumpHTML() + '</td>'
			s += '</tr></table>'

		return s

class VContainer(Container):
	def __init__(self, e=[]):
		Container.__init__(self)
		self.Elements = []
		self.Elements += e
		return

	def DumpHTML(self):
		s = ''
		if self.Visible:
			s += '<table cellspacing="0" cellpadding="0">'
			for e in self.Elements:
				s += '<tr><td>' + e.DumpHTML() + '</td></tr>'
			s += '</table>'

		return s


class SwitchContainer(Container):
	def Switch(self, ee):
		for e in self.Elements:
			e.Visible = False
		ee.Visible = True
		return


class Button(Element):
	Visible = True
	Text = ""

	def __init__(self, t = ''):
		Element.__init__(self)
		self.Text = t

	def DumpHTML(self):
		s = '<a href="#" onclick="javascript:ajax(\'/handle;' + self.ID + ';click;\');"><div class="ui-el-button">' + self.Text + '</div></a>';
		return s

class Link(Element):
	Visible = True
	Text = ""

	def __init__(self, t = ''):
		Element.__init__(self)
		self.Text = t

	def DumpHTML(self):
		s = '<a href="#" onclick="javascript:ajax(\'/handle;' + self.ID + ';click;\');"><span class="ui-el-link">' + self.Text + '</span></a>';
		return s

class Action(Element):
	Visible = True
	Text = ""
	Description = ""
	Icon = "go"

	def __init__(self, t = ''):
		Element.__init__(self)
		self.Text = t

	def DumpHTML(self):
		s = '<a href="#" onclick="javascript:ajax(\'/handle;' + self.ID + ';click;\');"><div class="ui-el-action"><table><tr><td rowspan="2" class="ui-el-action-icon"><img src="/dl;' + self.Icon + '.png" /></td><td class="ui-el-action-text">' + self.Text + '</td></tr><tr><td class="ui-el-action-description">' + self.Description + '</td></tr></table></div></a>';
		return s

class Label(Element):
	Visible = True
	Text = ""
	Size = 1

	def __init__(self, t = ''):
		Element.__init__(self)
		self.Text = t

	def DumpHTML(self):
		s = '<div class="ui-el-label-' + str(self.Size) + '">' + self.Text + '</div>';
		return s

class Input(Element):
	Visible = True
	Text = ""
	Size = 1

	def __init__(self, t = ''):
		Element.__init__(self)
		self.Text = t

	def DumpHTML(self):
		s = '<input class="ui-el-input" onblur="javascript:ajaxNoUpdate(\'/handle;' + self.ID + ';update;\'+escape(document.getElementById(\'' + self.ID + '\').value));" id="' + self.ID + '" value="' + self.Text + '"';
		if self.Disabled: s += ' disabled '
		s += '/>';
		return s

	def Handler(self, t, e, d):
		if e == 'update':
			self.Text = util.URLDecode(d)

class Checkbox(Element):
	Visible = True
	Text = ""
	Size = 1
	Checked = False

	def __init__(self, t = ''):
		Element.__init__(self)
		self.Text = t

	def DumpHTML(self):
		s = '<input type="checkbox" class="ui-el-checkbox" onclick="javascript:ajax(\'/handle;' + self.ID + ';click;\'+document.getElementById(\'' + self.ID + '\').value);" id="' + self.ID + '"';
		if self.Disabled: s += ' disabled'
		if self.Checked: s += ' checked'
		s += '/>';
		return s

	def Handler(self, t, e, d):
		if e == 'click':
			self.Checked = not self.Checked


class Radio(Element):
	Visible = True
	Text = ""
	Size = 1
	Checked = False
	Group = None

	def __init__(self, t = ''):
		Element.__init__(self)
		self.Text = t

	def DumpHTML(self):
		s = '<input type="radio" class="ui-el-radio" onclick="javascript:ajax(\'/handle;' + self.ID + ';click;\'+document.getElementById(\'' + self.ID + '\').value);" id="' + self.ID + '"';
		if self.Disabled: s += ' disabled'
		if self.Checked: s += ' checked'
		s += '/>';
		return s

	def Handler(self, t, e, d):
		if e == 'click':
			for e in self.Group.Elements:
				e.Elements[0].Checked = False
			self.Checked = True


class RadioGroup(VContainer):
	def __init__(self):
		Element.__init__(self)
		self.Elements = []
		return

	def Add(self, s):
		r = Radio()
		l = Label(s)
		r.Group = self
		self.AddElement(Container([r, l]))
		return

	def GetBox(self, i):
		return self.Elements[i].Elements[0]


class Image(Element):
	Visible = True
	File = ""

	def __init__(self, f = ''):
		Element.__init__(self)
		self.File = f

	def DumpHTML(self):
		s = '<img class="ui-el-image" src="/dl;' + self.File + '" />';
		return s

class ImageLabel(Element):
	Visible = True
	File = ""
	Text = ""
	Size = 1

	def __init__(self, f = '', t = ''):
		Element.__init__(self)
		self.File = f
		self.Text = t

	def DumpHTML(self):
		s = '<img class="ui-el-image-small" src="/dl;' + self.File + '" />';
		s += '<span class="ui-el-label-' + str(self.Size) + '">' + self.Text + '</span>';
		return s


class Spacer(Element):
	Visible = True
	Width = 1
	Height = 1

	def __init__(self, w = 1, h = 1):
		Element.__init__(self)
		self.Width = w
		self.Height = h

	def DumpHTML(self):
		s = '<div style="width:' + str(self.Width) + 'px; height:' + str(self.Height) + 'px;"></div>';
		return s

class Category(Element):
	Visible = True
	Text = ""
	Description = ""
	Icon = "plug/dashboard;icon-config"
	Selected = False

	def DumpHTML(self):
		s = '<a href="#" onclick="javascript:ajax(\'/handle;' + self.ID + ';click;\');"><div class="ui-el-category'
		if self.Selected: s += '-selected'
		s +='"><table><tr><td rowspan="2" class="ui-el-category-icon"><img src="/dl;' + self.Icon + '.png" /></td><td class="ui-el-category-text">' + self.Text + '</td></tr><tr><td class="ui-el-category-description">' + self.Description + '</td></tr></table></div></a>';
		return s

class MainWindow(Container):
	def __init__(self):
		Element.__init__(self)
		self.Elements = []
		return

	def DumpHTML(self):
		s = ''
		if self.Visible:
			s += '<table cellspacing="0" cellpadding="0" class="ui-el-mainwindow"><tr>'
			s += '<td class="ui-el-mainwindow-top" colspan="2">' + self.Elements[0].DumpHTML() + '</td></tr><tr>'
			s += '<td class="ui-el-mainwindow-left">' + self.Elements[1].DumpHTML() + '</td>'
			s += '<td class="ui-el-mainwindow-right">' + self.Elements[2].DumpHTML() + '</td>'
			s += '</tr></table>'

		return s

class TopBar(Element):
	Visible = True
	Text = ""

	def DumpHTML(self):
		s = '<span class="ui-logo"><img src="/dl;core;ui/logo.png" />' + self.Text + '</span>';
		return s


class LayoutTable(Element):
	Rows = []
	Widths = []

	def __init__(self, r=[]):
		Element.__init__(self)
		self.Rows = []
		self.Rows += r
		return

	def DumpHTML(self):
		s = ''
		if self.Visible:
			s += '<table cellspacing="0" cellpadding="2">'
			for e in self.Rows:
				e.Widths = self.Widths
				s += e.DumpHTML()
			s += '</table>'

		return s

	def Handle(self, target, event, data):
		Element.Handle(self, target, event, data)
		for e in self.Rows:
			e.Handle(target, event, data)


class LayoutTableRow(Element):
	Cells = []
	Widths = []
	Wide = 0

	def __init__(self, c=[], w=0):
		Element.__init__(self)
		self.Cells = []
		self.Cells += c
		self.Widths = []
		self.Wide = w
		return

	def DumpHTML(self):
		s = ''
		if self.Wide:
			self.Widths[0] = "auto"

		if self.Visible:
			s += '<tr>'
			i = 0
			for e in self.Cells:
				s += '<td'
				if not self.Wide == 0: s += ' colspan="' + str(self.Wide) + '" '
				s += ' width="' + str(self.Widths[i]) + '">' + e.DumpHTML() + '</td>'
				i += 1
			s += '</tr>'

		return s

	def Handle(self, target, event, data):
		Element.Handle(self, target, event, data)
		for e in self.Cells:
			e.Handle(target, event, data)



class SimpleBox(Element):
	Width = 100
	Height = 20
	Inner = None

	def __init__(self, e=Element()):
		Element.__init__(self)
		self.Inner = e
		return


	def DumpHTML(self):
		s = ''
		if self.Visible:
			s += '<div class="ui-el-modal-main"><table cellspacing="0" cellpadding="0"><tr><td class="ui-el-modal-lt"></td><td class="ui-el-modal-t"></td><td class="ui-el-modal-rt"></td></tr>'
			s += '<tr><td class="ui-el-modal-l"></td><td class="ui-el-modal-c" width="' + str(self.Width) + '" height="' + str(self.Height) + '">'
			s += self.Inner.DumpHTML()
			s += '</td><td class="ui-el-modal-r"></td></tr><tr><td class="ui-el-modal-lb"></td><td class="ui-el-modal-b"></td><td class="ui-el-modal-rb"></td></tr></table></div>'

		return s

	def Handle(self, target, event, data):
		Element.Handle(self, target, event, data)
		self.Inner.Handle(target, event, data)



class DialogBox(Element):
	Width = 500
	Height = "auto"
	Inner = None
	Buttons = None
	btnOK = None
	btnCancel = None
	lblTitle = None
	_content = None

	def __init__(self, e=Element()):
		Element.__init__(self)
		self.Inner = e
		self.btnOK = Button('OK')
		self.btnCancel = Button('Cancel')
		self.lblTitle = Label('Options')
		self.lblTitle.Size = 4
		self._content = VContainer([self.lblTitle, Spacer(1,10), Element()])
		self.Buttons = HContainer([Element(), self.btnOK, self.btnCancel])
		return


	def DumpHTML(self):
		s = ''
		if self.Visible:
			s += '<div class="ui-el-modal-main"><table cellspacing="0" cellpadding="0"><tr><td class="ui-el-modal-lt"></td><td class="ui-el-modal-t"></td><td class="ui-el-modal-rt"></td></tr>'
			s += '<tr><td class="ui-el-modal-l"></td><td class="ui-el-modal-c" width="' + str(self.Width) + '" height="' + str(self.Height) + '">'
			self._content.Elements[2] = self.Inner
			s += self._content.DumpHTML()
			s += '<div class="ui-el-modal-buttons">' + self.Buttons.DumpHTML() + '</div>'
			s += '</td><td class="ui-el-modal-r"></td></tr><tr><td class="ui-el-modal-lb"></td><td class="ui-el-modal-b"></td><td class="ui-el-modal-rb"></td></tr></table></div>'

		return s

	def Handle(self, target, event, data):
		Element.Handle(self, target, event, data)
		self.Buttons.Handle(target, event, data)
		self.Inner.Handle(target, event, data)



class DataTable(Element):
	Rows = []
	Widths = []
	NoStyle = False
	Title = ''
	_lblTitle = None

	def __init__(self, r=[]):
		Element.__init__(self)
		self._lblTitle = Label('')
		self.Rows = []
		self.Rows += r
		return

	def DumpHTML(self):
		s = ''
		if self.Visible:
			self._lblTitle.Text = self.Title
			s += self._lblTitle.DumpHTML() + '<br/>'
			s += '<table cellspacing="0" cellpadding="2" class="ui-el-table">'
			for e in self.Rows:
				e.Widths = self.Widths
				s += e.DumpHTML()
			s += '</table>'

		return s

	def Handle(self, target, event, data):
		Element.Handle(self, target, event, data)
		for e in self.Rows:
			e.Handle(target, event, data)


class DataTableRow(Element):
	Cells = []
	IsHeader = False
	Widths = []
	Wide = 0

	def __init__(self, c=[], w=0):
		Element.__init__(self)
		self.Cells = []
		self.Cells += c
		self.Widths = []
		self.Wide = w
		return

	def DumpHTML(self):
		s = ''
		if self.Wide:
			self.Widths[0] = "auto"

		if self.Visible:
			s += '<tr class="ui-el-table-row'
			if self.IsHeader: s += '-header'
			s += '">'
			i = 0
			for e in self.Cells:
				s += '<td class="ui-el-table-cell" '
				if not self.Wide == 0: s += ' colspan="' + str(self.Wide) + '" '
				s += ' width="' + str(self.Widths[i]) + '">' + e.DumpHTML() + '</td>'
				i += 1
			s += '</tr>'

		return s

	def Handle(self, target, event, data):
		Element.Handle(self, target, event, data)
		for e in self.Cells:
			e.Handle(target, event, data)

