from lxml import etree
import os.path

import xslt

class Layout:
    def __init__(self, file):
        self._dom = etree.parse(file)
        
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

    def appendChildInto(self, dest, child):
        self.append(dest, child)
        
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



