import random

class UI:

	Root = None
	UpdatedElement = None

	def DumpBasePage(self):
		s = ''#<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">';
		s += '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ru">'
		s += '<head><meta http-equiv="content-type" content="text/html; charset=utf-8" />'
		s += '<title>Ajenti alpha</title>'
		s += '<link href="/dl;core;ui.css" rel="stylesheet" media="all" />'
		s += '<link rel="shortcut icon" href="/dl;core;ui/favicon.png" />'
		s += '<script src="/dl;core;ajax.js"></script></head>\n<body id="main" onload="loadpage()">'
		s += '<script src="/dl;core;loadpage.js"></script>'
		s += "</body></html>"
		return s

	
	def DumpHTML(self):
		return self.Root.DumpHTML()

	#DEPRECATED
	def ResetUpdated(self):
		Root.ResetUpdated()



class Element(object):
	Visible = True
	ID = ''
	Handler = None

	#DEPRECATED
	Updated = False
	
	def __init__(self): 
		self.ID = str(random.randint(1, 9000*9000))
		print self.ID
		
	def DumpHTML(self):
		s = '<img src="dl;core;img.png" />'
		return s

	def Handle(self, target, event, data):
		if self.ID == target and not self.Handler == None:
			self.Handler(self, event, data)

	#DEPRECATED
	def ResetUpdated(self):
		self.Updated = False
		
	
class Container(Element):
	Elements = []
	
	def __init__(self):
		self.Elements = []
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
		
	#DEPRECATED
	def ResetUpdated(self):
		for e in self.Elements:
			e.ResetUpdated()


class HContainer(Container):
	def __init__(self):
		self.Elements = []
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
	def __init__(self):
		self.Elements = []
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


class Action(Element):
	Visible = True
	Text = ""
	Description = ""
	Icon = "go"
	
	def DumpHTML(self):
		s = '<a href="#" onclick="javascript:ajax(\'/handle;' + self.ID + ';click;\');"><div class="ui-el-action"><table><tr><td rowspan="2" class="ui-el-action-icon"><img src="/dl;core;ui/icon-' + self.Icon + '.png" /></td><td class="ui-el-action-text">' + self.Text + '</td></tr><tr><td class="ui-el-action-description">' + self.Description + '</td></tr></table></div></a>';
		return s

class Label(Element):
	Visible = True
	Text = ""
	
	def DumpHTML(self):
		s = '<span class="ui-el-label">' + self.Text + '</span>';
		return s



class MainWindow(Container):
	def __init__(self):
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
	

