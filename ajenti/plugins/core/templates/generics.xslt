<xsl:template match="container">
    <xsl:apply-templates />
</xsl:template>

<xsl:template match="hcontainer">
    <table cellspacing="0" cellpadding="0" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
         <tr>
             <xsl:for-each select="*">
                <td style="padding-right: {x:css(../@spacing, '4')}">
                    <xsl:apply-templates select="." />
                </td>
             </xsl:for-each>    
         </tr>
    </table>
</xsl:template>

<xsl:template match="vcontainer">
     <table cellspacing="0" cellpadding="0" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
         <xsl:for-each select="*">
             <tr><td style="padding-bottom: {x:css(../@spacing, '4')}">  
                 <xsl:apply-templates select="."/>
             </td></tr>
         </xsl:for-each>    
    </table>
</xsl:template>


<xsl:template match="spacer">
    <div style="width: {x:css(@width, '1')}; height: {x:css(@height, '1')};" />
</xsl:template>


<xsl:template match="scrollcontainer">
    <div class="ui-el-scrollcontainer" style="width: {x:css(@width, '200')}; height: {x:css(@height, '200')};">
        <xsl:apply-templates />
    </div>
</xsl:template>
