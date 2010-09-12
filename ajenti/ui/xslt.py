from lxml import etree
from lxml.etree import *

xslt = None

def prepare(includes):
    global xslt
    xml = XSLT % ''.join([open(x).read() for x in includes])
    xslt = etree.XSLT(etree.fromstring(xml))
        
def render(templ):
    return etree.tostring(xslt(templ))
    
XSLT="""
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

  <xsl:template match="xml">
      <xsl:apply-templates />
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


