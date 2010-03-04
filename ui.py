import random

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

	def __init__(self):
		self.ID = str(random.randint(1, 9000*9000))

	def DumpHTML(self):
		s = '<img src="dl;core;img.png" />'
		return s

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

class Button(Element):
	Visible = True
	Text = ""

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


class Table(Element):
	Rows = []

	def __init__(self, r=[]):
		Element.__init__(self)
		self.Rows = []
		self.Rows += r
		return

	def DumpHTML(self):
		s = ''
		if self.Visible:
			s += '<table cellspacing="0" cellpadding="0" class="ui-el-table">'
			for e in self.Rows:
				s += e.DumpHTML()
			s += '</table>'

		return s

	def Handle(self, target, event, data):
		Element.Handle(self, target, event, data)
		for e in self.Rows:
			e.Handle(target, event, data)


class TableRow(Element):
	Cells = []
	IsHeader = False
	Widths = []

	def __init__(self, c=[]):
		Element.__init__(self)
		self.Cells = []
		self.Cells += c
		self.Widths = []
		return

	def DumpHTML(self):
		s = ''
		if self.Visible:
			s += '<tr class="ui-el-table-row'
			if self.IsHeader: s += '-header'
			s += '">'
			i = 0
			for e in self.Cells:
				s += '<td class="ui-el-table-cell" width="' + str(self.Widths[i]) + '">' + e.DumpHTML() + '</td>'
				i += 1
			s += '</tr>'

		return s

	def Handle(self, target, event, data):
		Element.Handle(self, target, event, data)
		for e in self.Cells:
			e.Handle(target, event, data)
