import os.path
from lxml import etree
from lxml.etree import *

from ajenti.ui import UI


EMPTY_TEMPLATE='<html xmlns="http://www.w3.org/1999/xhtml" />'
EMPTY_XSLT="""
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" indent="yes" encoding="UTF-8"/>
  
  <xsl:template match="@*|node()">
     <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
     </xsl:copy>
  </xsl:template>

  <xsl:template match="html">
      <html xmlns="http://www.w3.org/1999/xhtml">
          <xsl:apply-templates />
      </html>
  </xsl:template>
  
  <xsl:template match="headstylesheets">
     <xsl:for-each select="headstylesheet">
         <link href="{@href}" rel="stylesheet" media="all" />
     </xsl:for-each>
  </xsl:template>

  <xsl:template match="headscripts">
     <xsl:for-each select="headscript">
         <script src="{@href}">
         </script>
     </xsl:for-each>
  </xsl:template>
  
  %s
  
</xsl:stylesheet>  
"""

class BasicTemplate(object):
    def __init__(self, filename=None, search_path=[], includes=[], vars={}):
        self.search_path = search_path

        if filename is not None:
            for p in search_path:
                if os.path.isfile(os.path.join(p, filename)):
                    filename = os.path.join(p, filename)

            self._dom = etree.parse(filename)
        else:
            self._dom = etree.fromstring(EMPTY_TEMPLATE)

        self.includes = includes
        self.vars = vars

    def appendChildInto(self, dest, child):
        """ Tries to append child element to given tag
        @dest - destination tag to append to
        @child - child DOM element
        """
        el = self._dom.find('.//%s'%dest)
        if el is not None:
            el.append(child)
        else:
            raise RuntimeError("Tag <%s> not found"%dest)

    def elements(self):
        return self._dom.getroot()

    def render(self, *args, **kwargs):
        xslt = EMPTY_XSLT % ''.join([open(x).read() for x in self.includes])
        xslt = etree.XSLT(etree.fromstring(xslt))
        
        for x in self.vars['styles']:
            self._dom.find('.//headstylesheets').append(etree.Element('headstylesheet', href=x))
        for x in self.vars['scripts']:
            self._dom.find('.//headscripts').append(etree.Element('headscript', href=x))

        return etree.tostring(xslt(self._dom))
