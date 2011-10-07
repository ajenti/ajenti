<xsl:template match="customhtml">
    <div id="{@id}" />
    <script>
         ui_fill_custom_html('<xsl:value-of select="@id"/>', '<xsl:value-of select="x:b64(@html)"/>');
    </script> 
</xsl:template>

<xsl:template match="js">
    <script>
        <xsl:value-of select="@code"/>
    </script> 
</xsl:template>

<xsl:template match="null">
</xsl:template>

<xsl:template match="headtitle">
    <title><xsl:value-of select="@text"/></title>
</xsl:template>

<xsl:template match="completerefresh">
    <script>document.location.href="/";</script>
</xsl:template>

<xsl:template match="container">
    <div style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
           <xsl:apply-templates />
    </div>
</xsl:template>

<xsl:template match="pad">
    <div class="ui-el-pad">
           <xsl:apply-templates />
    </div>
</xsl:template>

<xsl:template match="hcontainer">
    <table class="layout" style="display: inline-block; width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
         <tr>
             <xsl:for-each select="*">
                <td style="padding-right: {x:css(../@spacing, '0')}">
                    <xsl:apply-templates select="." />
                </td>
             </xsl:for-each>    
         </tr>
    </table>
</xsl:template>

<xsl:template match="vcontainer">
     <table class="layout"  style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
         <xsl:for-each select="*">
             <tr><td style="padding-bottom: {x:css(../@spacing, '0')}">  
                 <xsl:apply-templates select="."/>
             </td></tr>
         </xsl:for-each>    
    </table>
</xsl:template>


<xsl:template match="spacer">
    <div style="width: {x:css(@width, '1')}; height: {x:css(@height, '1')};" />
</xsl:template>


<xsl:template match="scrollcontainer">
    <div class="ui-el-scrollcontainer" style="width: {x:css(@width, '200')}; height: {x:css(@height, '200')}; {x:iif(@noborder, 'border: none', '')}">
        <xsl:apply-templates />
    </div>
</xsl:template>
