from lxml import etree
from lxml.etree import *


xslt = None

def prepare(includes, funcs):
    global xslt, xslt2
    xml = XSLT % ''.join([open(x).read() for x in includes])
    
    ex = {}
    for x in funcs:
        ex[('x', x)] = funcs[x]

    xslt = etree.XSLT(etree.fromstring(xml), extensions=ex)
    xslt2 = etree.XSLT(etree.fromstring(XSLT2), extensions=ex)
        
def render(templ):
    global xslt, xslt2
    return etree.tostring(xslt2(xslt(xslt(templ))), method="html", pretty_print=True) #!!!
    
    

XSLT="""<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns:x="x"
    xmlns:h="h"
    extension-element-prefixes="x">
    
  <xsl:output method="html" doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd" encoding="utf-8" />

  <xsl:template match="@*|node()">
     <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
     </xsl:copy>
  </xsl:template>

  <xsl:template match="html">
      <html xmlns="http://www.w3.org/1999/xhtml" class="{@class}">
          <xsl:apply-templates />
      </html>
  </xsl:template>

  <xsl:template match="xml">
      <xsl:apply-templates />
  </xsl:template>
  
  <xsl:template match="headstylesheets">
     <xsl:for-each select="headstylesheet">
         <link href="{@href}" rel="stylesheet/less" />
     </xsl:for-each>
  </xsl:template>

  <xsl:template match="headscripts">
     <xsl:for-each select="headscript">
         <script src="{@href}">
            <xsl:text> </xsl:text>
         </script>
     </xsl:for-each>
  </xsl:template>
  
  %s
  
</xsl:stylesheet>  
"""


XSLT2 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns:x="x"
    extension-element-prefixes="x">
    
  <xsl:output method="html" doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd" encoding="utf-8" />

  <xsl:template match="@*|node()">
     <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
     </xsl:copy>
  </xsl:template>

  <xsl:template match="hlabel">
     <label for="{@for}" class="{@class}"><xsl:value-of select="@text" /><xsl:apply-templates /></label>
  </xsl:template>
</xsl:stylesheet>  
"""
