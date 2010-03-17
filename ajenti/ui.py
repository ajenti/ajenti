import random
import xml.dom.minidom as dom

from ajenti.com import *

class Document(object):
    def __init__(self, elements=[]):
        di = dom.getDOMImplementation('')
        dt = di.createDocumentType('html', '-//W3C//DTD XHTML 1.0 Strict//EN', 
                            'http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd')
        self.document = di.createDocument('http://www.w3.org/1999/xhtml', 
                                          'html', dt)
        html = self.document.getElementsByTagName('html')[0]

        head = dom.Element('head')

        meta = dom.Element('meta')
        meta.setAttribute('http-equiv', 'content-type')
        meta.setAttribute('content', 'text/html')
        meta.setAttribute('charset', 'utf-8')
        head.appendChild(meta)

        title = dom.Element('title')
        t = self.document.createTextNode('Ajenti alpha')
        title.appendChild(t)
        head.appendChild(title)

        link = dom.Element('link')
        link.setAttribute('href', '/dl/core/ui.css')
        link.setAttribute('rel', 'stylesheet')
        link.setAttribute('media', 'all')
        head.appendChild(link)

        link = dom.Element('link')
        link.setAttribute('href', '/dl/core/ui/favicon.png')
        link.setAttribute('rel', 'shortcut icon')
        head.appendChild(link)

        script = dom.Element('script')
        script.setAttribute('src', '/dl/core/ajax.js')
        t = self.document.createTextNode('')
        script.appendChild(t)
        head.appendChild(script)

        body = dom.Element('body')
        body.setAttribute('id', 'main')

        for el in elements:
            body.appendChild(el)

        html.appendChild(head)
        html.appendChild(body)

    def toxml(self):
        return self.document.toxml()

    def toprettyxml(self, spacer='\t'):
        return self.document.toprettyxml(spacer)


class Element(dom.Element):
    visible = True

    def __init__(self, tag):
        dom.Element.__init__(self, tag)
        self.id = str(random.randint(1, 9000*9000))

class Category(Element):
    def __init__(self, text='Cat1', description='Default description',
                       icon='core/default.png', selected=False):
        Element.__init__(self, 'a')
        self.setAttribute('href','#');
        self.setAttribute('onclick',
                          "javascript:ajax('/handle/%s/click')"%self.id)

        div = dom.Element('div')
        if (selected):
            div.setAttribute('class', 'ui-el-category-selected')
        else:
            div.setAttribute('class', 'ui-el-category')

        self.appendChild(div)

        table = dom.Element('table')
        div.appendChild(table)

        tr = dom.Element('tr')
        table.appendChild(tr)

        td = dom.Element('td')
        td.setAttribute('rowspan', '2')
        td.setAttribute('class', 'ui-el-category-icon')
        tr.appendChild(td)

        img = dom.Element('img')
        img.setAttribute('src', '/dl/%s'%icon)
        td.appendChild(img)

        td = dom.Element('td')
        td.setAttribute('class', 'ui-el-category-text')
        d = dom.Document()
        t = d.createTextNode(text)
        td.appendChild(t)
        tr.appendChild(td)

        tr = dom.Element('tr')
        table.appendChild(tr)

        td = dom.Element('td')
        td.setAttribute('class', 'ui-el-category-description')
        t = d.createTextNode(description)
        td.appendChild(t)
        tr.appendChild(td)

class VContainer(Element):
    container = None

    def __init__(self):
        Element.__init__(self, 'table')
        self.setAttribute('cellspacing', '0')
        self.setAttribute('cellpadding', '0')

        tr = dom.Element('tr')
        # Because we overrided this method
        Element.appendChild(self, tr)

        self.container = tr

    def appendChild(self, el):
        if el is not None:
            td = dom.Element('td')
            td.appendChild(el)
            self.container.appendChild(td)

class MainWindow(Element):
    top_container = None
    left_container = None
    right_container = None
    def __init__(self):
        Element.__init__(self, 'table')
        self.setAttribute('cellspacing', '0')
        self.setAttribute('cellpadding', '0')
        self.setAttribute('class', 'ui-el-mainwindow')

        tr = dom.Element('tr')
        self.appendChild(tr)
    
        td = dom.Element('td')
        td.setAttribute('class', 'ui-el-mainwindow-top')
        td.setAttribute('colspan', '2')
        tr.appendChild(td)

        self.top_container = td

        tr = dom.Element('tr')
        self.appendChild(tr)
        
        td = dom.Element('td')
        td.setAttribute('class', 'ui-el-mainwindow-left')
        tr.appendChild(td)

        self.left_container = td

        td = dom.Element('td')
        td.setAttribute('class', 'ui-el-mainwindow-right')
        tr.appendChild(td)

        self.right_container = td

    def top(self, el):
        self.top_container.appendChild(el)

    def left(self, el):
        self.left_container.appendChild(el)

    def right(self, el):
        self.right_container.appendChild(el)

class TopBar(Element):
    def __init__(self):
        Element.__init__(self, 'span')
        self.setAttribute('class', 'ui-logo')
        img = dom.Element('img')
        img.setAttribute('src', '/dl/core/ui/logo.png')
        self.appendChild(img)

