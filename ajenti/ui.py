import random
import util

class UI:
	root = None
	update_timer = 0

	def dump_base_page(self):
		s = ''#<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">';
		s += '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ru">'
		s += '<head><meta http-equiv="content-type" content="text/html; charset=utf-8" />'
		s += '<title>Ajenti alpha</title>'
		s += '<link href="/dl;core;ui.css" rel="stylesheet" media="all" />'
		s += '<link rel="shortcut icon" href="/dl;core;ui/favicon.png" />'
		s += '<script src="/dl;core;ajax.js"></script></head>\n<body id="main">'
		s += self.dump_HTML()
		s += "</body></html>"
		return s

	def dump_HTML(self):
		s = self.root.dump_HTML()
		s += '<!-- update=' + str(self.update_timer) + ' -->'
		self.update_timer = 0
		return s


class Element(object):
	visible = True
	id = ''
	handler = None
	disabled = False

	def __init__(self):
		self.id = str(random.randint(1, 9000*9000))

	def dump_HTML(self):
		return ''

	def handle(self, target, event, data):
		if self.id == target and not self.handler == None:
			self.handler(self, event, data)


class Container(Element):
	elements = []

	def __init__(self, e=[]):
		Element.__init__(self)
		self.elements = []
		self.elements += e
		return

	def clear(self):
		self.elements = []
		return

	def add_element(self, e):
		self.elements.append(e)
		return

	def remove_element(self, e):
		self.elements.remove(e)
		return

	def handle(self, target, event, data):
		Element.handle(self, target, event, data)
		for e in self.elements:
			if e.visible:
				e.handle(target, event, data)

	def dump_HTML(self):
		s = ''
		if self.visible:
			for e in self.elements:
				if e.visible:
					s += e.dump_HTML()

		return s


class HContainer(Container):
	def dump_HTML(self):
		s = ''
		if self.visible:
			s += '<table cellspacing="0" cellpadding="0"><tr>'
			for e in self.elements:
				if e.visible:
					s += '<td>' + e.dump_HTML() + '</td>'
			s += '</tr></table>'
		return s


class VContainer(Container):
	def dump_HTML(self):
		s = ''
		if self.visible:
			s += '<table cellspacing="0" cellpadding="0">'
			for e in self.elements:
				if e.visible:
					s += '<tr><td>' + e.dump_HTML() + '</td></tr>'
			s += '</table>'
		return s


class SwitchContainer(Container):
	def switch(self, ee):
		for e in self.elements:
			e.visible = False
		ee.visible = True
		return


class ScrollContainer(Container):
	width = 100
	height = 100

	def dump_HTML(self):
		return '<div class="ui-el-scrollcontainer" style="width:' + str(self.width) + \
			'px; height:' + str(self.height) + 'px;">' + Container.dump_HTML(self) + '</div>'


class Button(Element):
	text = ""

	def __init__(self, t=''):
		Element.__init__(self)
		self.text = t

	def dump_HTML(self):
		s = '<a href="#" onclick="javascript:ajax(\'/handle;' + self.id + ';click;\');">' + \
			'<div class="ui-el-button">' + self.text + '</div></a>';
		return s


class Link(Element):
	text = ""

	def __init__(self, t=''):
		Element.__init__(self)
		self.text = t

	def dump_HTML(self):
		s = '<a href="#" onclick="javascript:ajax(\'/handle;' + self.id + ';click;\');">' + \
			'<span class="ui-el-link">' + self.text + '</span></a>';
		return s


class Action(Element):
	text = ""
	description = ""
	icon = "go"

	def __init__(self, t=''):
		Element.__init__(self)
		self.text = t

	def dump_HTML(self):
		s = '<a href="#" onclick="javascript:ajax(\'/handle;' + self.id + ';click;\');">' + \
			'<div class="ui-el-action"><table><tr><td rowspan="2" class="ui-el-action-icon">' + \
			'<img src="/dl;' + self.icon + '.png" /></td><td class="ui-el-action-text">' + \
			self.text + '</td></tr><tr><td class="ui-el-action-description">' + \
			self.description + '</td></tr></table></div></a>';
		return s


class Label(Element):
	text = ""
	size = 1

	def __init__(self, t=''):
		Element.__init__(self)
		self.text = t

	def dump_HTML(self):
		s = '<div class="ui-el-label-' + str(self.size) + '">' + self.text + '</div>';
		return s


class Input(Element):
	text = ""

	def __init__(self, t=''):
		Element.__init__(self)
		self.text = t

	def dump_HTML(self):
		s = '<input class="ui-el-input" onblur="javascript:ajaxNoUpdate(\'/handle;' + self.id + \
			';update;\'+escape(document.getElementById(\'' + self.id + '\').value));" id="' + \
			self.id + '" value="' + self.text + '"';
		if self.disabled: s += ' disabled '
		s += '/>';
		return s

	def handler(self, t, e, d):
		if e == 'update':
			self.text = util.url_decode(d)


class Checkbox(Element):
	checked = False

	def dump_HTML(self):
		s = '<input type="checkbox" class="ui-el-checkbox" onclick="javascript:ajax(\'/handle;' + \
			self.id + ';click;\'+document.getElementById(\'' + self.id + '\').value);" id="' + \
			self.id + '"';
		if self.disabled: s += ' disabled'
		if self.checked: s += ' checked'
		s += '/>';
		return s

	def handler(self, t, e, d):
		if e == 'click':
			self.checked = not self.checked


class Radio(Element):
	checked = False
	group = None

	def dump_HTML(self):
		s = '<input type="radio" class="ui-el-radio" onclick="javascript:ajax(\'/handle;' + \
			self.id + ';click;\'+document.getElementById(\'' + self.id + '\').value);" id="' + \
			self.id + '"';
		if self.disabled: s += ' disabled'
		if self.checked: s += ' checked'
		s += '/>';
		return s

	def handler(self, t, e, d):
		if e == 'click':
			for e in self.group.elements:
				e.elements[0].checked = False
			self.checked = True


class RadioGroup(VContainer):
	def add(self, s):
		r = Radio()
		l = Label(s)
		r.group = self
		self.add_element(Container([r, l]))
		return

	def get_box(self, i):
		return self.elements[i].elements[0]


class Image(Element):
	file = ""

	def __init__(self, f=''):
		Element.__init__(self)
		self.file = f

	def dump_HTML(self):
		s = '<img class="ui-el-image" onclick="javascript:ajax(\'/handle;' + self.id + ';click;\');" src="/dl;' + self.file + '" />';
		return s


class ImageLabel(Element):
	file = ""
	text = ""
	size = 1

	def __init__(self, f='', t=''):
		Element.__init__(self)
		self.file = f
		self.text = t

	def dump_HTML(self):
		s = '<img class="ui-el-image-small" src="/dl;' + self.file + '" />';
		s += '<span class="ui-el-label-' + str(self.size) + '">' + self.text + '</span>';
		return s


class Spacer(Element):
	width = 1
	height = 1

	def __init__(self, w=1, h=1):
		Element.__init__(self)
		self.width = w
		self.height = h

	def dump_HTML(self):
		s = '<div style="width:' + str(self.width) + 'px; height:' + str(self.height) + 'px;"></div>';
		return s


class Category(Element):
	text = ""
	description = ""
	icon = "plug/dashboard;icon-config"
	selected = False

	def dump_HTML(self):
		s = '<a href="#" onclick="javascript:ajax(\'/handle;' + self.id + \
			';click;\');"><div class="ui-el-category'
		if self.selected: s += '-selected'
		s += '"><table><tr><td rowspan="2" class="ui-el-category-icon"><img src="/dl;' + \
			self.icon + '.png" /></td><td class="ui-el-category-text">' + self.text + \
			'</td></tr><tr><td class="ui-el-category-description">' + self.description + \
			'</td></tr></table></div></a>';
		return s


class MainWindow(Container):
	def dump_HTML(self):
		s = ''
		if self.visible:
			s += '<table cellspacing="0" cellpadding="0" class="ui-el-mainwindow"><tr>'
			s += '<td class="ui-el-mainwindow-top" colspan="2">' + self.elements[0].dump_HTML() + '</td></tr><tr>'
			s += '<td class="ui-el-mainwindow-left">' + self.elements[1].dump_HTML() + '</td>'
			s += '<td class="ui-el-mainwindow-right">' + self.elements[2].dump_HTML() + '</td>'
			s += '</tr></table>'

		return s


class TopBar(Element):
	def dump_HTML(self):
		s = '<span class="ui-logo"><img src="/dl;core;ui/logo.png" /></span>';
		return s


class LayoutTable(Element):
	rows = []
	widths = []

	def __init__(self, r=[]):
		Element.__init__(self)
		self.rows = []
		self.rows += r
		return

	def dump_HTML(self):
		s = ''
		if self.visible:
			s += '<table cellspacing="0" cellpadding="2">'
			for e in self.rows:
				e.widths = self.widths
				if e.visible:
					s += e.dump_HTML()
			s += '</table>'

		return s

	def handle(self, target, event, data):
		Element.handle(self, target, event, data)
		for e in self.rows:
			e.handle(target, event, data)


class LayoutTableRow(Element):
	cells = []
	widths = []
	wide = 0

	def __init__(self, c=[], w=0):
		Element.__init__(self)
		self.cells = c
		self.widths = []
		self.wide = w
		return

	def dump_HTML(self):
		s = ''
		if self.wide:
			self.widths[0] = "auto"

		s += '<tr>'
		i = 0
		for e in self.cells:
			if e.visible:
				s += '<td style="padding: 3px;"'
				if self.wide != 0:
					s += ' colspan="' + str(self.wide) + '" '
				s += ' width="' + str(self.widths[i]) + '">' + e.dump_HTML() + '</td>'
			i += 1
		s += '</tr>'
		return s

	def handle(self, target, event, data):
		Element.handle(self, target, event, data)
		for e in self.cells:
			e.handle(target, event, data)

"""
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
"""


class DialogBox(Element):
	width = 500
	height = "auto"
	inner = None
	buttons = None
	btnOK = None
	btnCancel = None
	lblTitle = None
	_content = None

	def __init__(self, e=Element()):
		Element.__init__(self)
		self.inner = e
		self.btnOK = Button('OK')
		self.btnCancel = Button('Cancel')
		self.lblTitle = Label('Options')
		self.lblTitle.size = 4
		self._content = VContainer([self.lblTitle, Spacer(1,10), Element()])
		self.buttons = HContainer([self.btnOK, self.btnCancel])
		return


	def dump_HTML(self):
		s = ''
		if self.visible:
			s += '<div class="ui-el-modal-main"><table cellspacing="0" cellpadding="0"><tr><td class="ui-el-modal-lt"></td><td class="ui-el-modal-t"></td><td class="ui-el-modal-rt"></td></tr>'
			s += '<tr><td class="ui-el-modal-l"></td><td class="ui-el-modal-c" width="' + str(self.width) + '" height="' + str(self.height) + '">'
			self._content.elements[2] = self.inner
			s += self._content.dump_HTML()
			s += '<div class="ui-el-modal-buttons">' + self.buttons.dump_HTML() + '</div>'
			s += '</td><td class="ui-el-modal-r"></td></tr><tr><td class="ui-el-modal-lb"></td><td class="ui-el-modal-b"></td><td class="ui-el-modal-rb"></td></tr></table></div>'

		return s

	def handle(self, target, event, data):
		Element.handle(self, target, event, data)
		self.buttons.handle(target, event, data)
		self.inner.handle(target, event, data)


class DataTable(Element):
	rows = []
	widths = []
	title = ''
	_lblTitle = None

	def __init__(self, r=[]):
		Element.__init__(self)
		self._lblTitle = Label('')
		self.rows = []
		self.rows += r
		return

	def dump_HTML(self):
		s = ''
		if self.visible:
			self._lblTitle.text = self.title
			s += self._lblTitle.dump_HTML() + '<br/>'
			s += '<table cellspacing="0" cellpadding="2" class="ui-el-table">'
			for e in self.rows:
				e.widths = self.widths
				if e.visible:
					s += e.dump_HTML()
			s += '</table>'

		return s

	def handle(self, target, event, data):
		Element.handle(self, target, event, data)
		for e in self.rows:
			e.handle(target, event, data)


class DataTableRow(Element):
	cells = []
	is_header = False
	widths = []
	wide = 0

	def __init__(self, c=[], w=0):
		Element.__init__(self)
		self.cells = c
		self.w= []
		self.wide = w
		return

	def dump_HTML(self):
		s = ''
		if self.wide:
			self.widths[0] = "auto"

		s += '<tr class="ui-el-table-row'
		if self.is_header: s += '-header'
		s += '">'
		i = 0
		for e in self.cells:
			if e.visible:
				s += '<td class="ui-el-table-cell" '
				if not self.wide == 0: s += ' colspan="' + str(self.wide) + '" '
				s += ' width="' + str(self.widths[i]) + '">' + e.dump_HTML() + '</td>'
			i += 1
		s += '</tr>'
		return s

	def handle(self, target, event, data):
		Element.handle(self, target, event, data)
		for e in self.cells:
			e.handle(target, event, data)


class TreeContainer(VContainer):
	pass


class TreeContainerNode(VContainer):
	text = ""
	expanded = ""
	_img = None

	def __init__(self, t=''):
		VContainer.__init__(self)
		self.text = t
		self._img = Image('')
		self._img.handler = self._on_clicked

	def dump_HTML(self):
		self._img.file = 'core;ui/tree-minus.png' if self.expanded else 'core;ui/tree-plus.png'
		s = '<div class="ui-el-treecontainernode"><div class="ui-el-treecontainernode-button"><a href="#">' + self._img.dump_HTML() + '</a></div>' + self.text
		if self.expanded:
			s += '<div class="ui-el-treecontainernode-inner">' + VContainer.dump_HTML(self) + '</div>'
		s += '</div>'
		return s

	def handle(self, target, event, data):
		VContainer.handle(self, target, event, data)
		self._img.handle(target, event, data)

	def _on_clicked(self, target, event, data):
		print 'asd'
		if event == 'click':
			self.expanded = not self.expanded


class TextArea(Element):
	text = ""
	width = "auto"
	height = "auto"

	def __init__(self, t=''):
		Element.__init__(self)
		self.text = t

	def dump_HTML(self):
		s = '<textarea class="ui-el-textarea" onblur="javascript:ajaxNoUpdate(\'/handle;' + self.id + \
			';update;\'+escape(document.getElementById(\'' + self.id + '\').value));" id="' + \
			self.id + '"';
		if self.disabled: s += ' disabled '
		s += 'style="width:' + str(self.width) + 'px; height:' + str(self.height) + 'px;">' + self.text + "</textarea>";
		return s

	def handler(self, t, e, d):
		if e == 'update':
			self.text = util.url_decode(d)
