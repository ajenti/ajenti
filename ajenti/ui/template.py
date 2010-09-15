import os.path
from lxml import etree
from lxml.etree import *
import xslt


class BasicTemplate(object):
    def __init__(self, filename, search_path=[], styles=[], scripts=[]):
        for p in search_path:
            if os.path.isfile(os.path.join(p, filename)):
                filename = os.path.join(p, filename)
        self._dom = etree.parse(filename)

        try:
            for x in styles:
                self._dom.find('.//headstylesheets').append(etree.Element('headstylesheet', href=x))
            for x in scripts:
                self._dom.find('.//headscripts').append(etree.Element('headscript', href=x))
        except:
            pass

    def appendChildInto(self, dest, child):
        el = self._dom.find('//*[@id=\'%s\']'%dest)
        if el is not None:
            el.append(child)
        else:
            raise RuntimeError("Tag with id=%s not found"%dest)

    def elements(self):
        return self._dom.getroot()

    def render(self):
        return xslt.render(self._dom.getroot())        

