from lxml import etree
from classes import *
import os.path
import xslt

class Layout:
    """
    An XML user interface layout storage. Loads layout data from `file`.
    """

    def __init__(self, file):
        parser = etree.XMLParser()
        parser.set_element_class_lookup(Lookup())
        self._dom = etree.parse(file, parser=parser)

    def find(self, id):
        """
        Finds a child element by `id` attribute.
        """
        el = self._dom.find('//*[@id=\'%s\']'%id)
        return el

    def remove(self, id):
        """
        Removes a child element by `id` attribute.
        """
        el = self.find(id)
        el.getparent().remove(el)

    def xpath(self, path):
        """
        Performs an XPath query on the tree.
        """
        return self._dom.find(path)

    def append(self, dest, child):
        """
        Appends `child` to a tag with `id`=`dest`.
        """
        el = self.find(dest)
        if el is not None:
            if isinstance(child, Layout):
                child = child.elements()
            el.append(child)
        else:
            raise RuntimeError("Tag with id=%s not found"%dest)

    def appendAll(self, dest, *args):
        """
        Appends `*args` to a tag with `id`=`dest`.
        """
        for a in args:
            self.append(dest, a)

    def insertText(self, dest, text):
        """
        Sets node's text.
        """
        self.find(dest).text = text

    def elements(self):
        """
        Returns root element.
        """
        return self._dom.getroot()

    def render(self):
        """
        Renders HTML into a string.
        """
        return xslt.render(self._dom.getroot())


class BasicTemplate(Layout):

    def __init__(self, filename, search_path=[], styles=[], scripts=[]):
        for p in search_path:
            if os.path.isfile(os.path.join(p, filename)):
                filename = os.path.join(p, filename)
        Layout.__init__(self, filename)

        # Fill in CSS and JS refs
        try:
            for x in sorted(styles):
                self._dom.find('.//headstylesheets').append(etree.Element('headstylesheet', href=x))
            for x in sorted(scripts):
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
