<xsl:template match="widget">
    <div height="{x:attr(@height, '')}" class="ui-el-widget">
        <xsl:apply-templates />
    </div>
</xsl:template>

