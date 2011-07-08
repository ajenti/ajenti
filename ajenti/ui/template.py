from lxml import etree
from classes import *
import os.path
import xslt

class Layout:
    def __init__(self, file):
        parser = etree.XMLParser()
        parser.set_element_class_lookup(Lookup())
        self._dom = etree.parse(file, parser=parser)
        
    def find(self, id):
        el = self._dom.find('//*[@id=\'%s\']'%id)
        return el

    def remove(self, id):
        el = self.find(id)
        el.getparent().remove(el)
                
    def xpath(self, path):
        return self._dom.find(path)
        
    def append(self, dest, child):
        el = self.find(dest)
        if el is not None:
            if isinstance(child, Layout):
                child = child.elements()
            el.append(child)
        else:
            raise RuntimeError("Tag with id=%s not found"%dest)

    def appendAll(self, dest, *args):
        for a in args:
            self.append(dest, a)
            
    def appendChildInto(self, dest, child):
        self.append(dest, child)
        
    def insertText(self, dest, text):
        self.find(dest).text = text
    
    def elements(self):
        return self._dom.getroot()

    def render(self):
        return xslt.render(self._dom.getroot())        

    
class BasicTemplate(Layout):

    def __init__(self, filename, search_path=[], styles=[], scripts=[]):
        for p in search_path:
            if os.path.isfile(os.path.join(p, filename)):
                filename = os.path.join(p, filename)
        Layout.__init__(self, filename)

        # Fill in CSS and JS refs
        try:
            for x in styles:
                self._dom.find('.//headstylesheets').append(etree.Element('headstylesheet', href=x))
            for x in scripts:
                self._dom.find('.//headscripts').append(etree.Element('headscript', href=x))
        except:
            pass


class Lookup(etree.CustomElementClassLookup):
    def lookup(self, node_type, document, namespace, name):
        if node_type != 'element':
            return None
        ovs = UI.list_overrides()
        if name in ovs:
            return ovs[name]
        return Element
        
