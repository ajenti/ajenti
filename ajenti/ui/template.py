import os.path
from lxml import etree
from lxml.etree import *
import xslt


EMPTY_TEMPLATE='<html xmlns="http://www.w3.org/1999/xhtml" />'


class BasicTemplate(object):
    def __init__(self, filename=None, search_path=[], styles=[], scripts=[]):
        self.search_path = search_path

        if filename is not None:
            for p in search_path:
                if os.path.isfile(os.path.join(p, filename)):
                    filename = os.path.join(p, filename)

            self._dom = etree.parse(filename)
        else:
            self._dom = etree.fromstring(EMPTY_TEMPLATE)
        try:
            for x in styles:
                self._dom.find('.//headstylesheets').append(etree.Element('headstylesheet', href=x))
            for x in scripts:
                self._dom.find('.//headscripts').append(etree.Element('headscript', href=x))
        except Exception,e:
            print e

    def appendChildInto(self, dest, child):
        el = self._dom.find('.//%s'%dest)
        if el is not None:
            el.append(child)
        else:
            raise RuntimeError("Tag <%s> not found"%dest)

    def elements(self):
        return self._dom.getroot()

    def render(self):
        return xslt.render(self._dom.getroot())        

