<xsl:template match="logviewer">
    <div class="ui-el-logviewer" style="width: {x:css(@width, '200')}; height: {x:css(@height, '200')};">
        <xsl:apply-templates />
     </div>
</xsl:template>

