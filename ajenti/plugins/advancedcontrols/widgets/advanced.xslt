<xsl:template match="sortlist">
    <div id="{@id}" class="ui-el-sortlist">
        <xsl:apply-templates />
    </div>
    <script>
        ui_initSortList('<xsl:value-of select="@id"/>');
    </script>
</xsl:template>

<xsl:template match="sortlistitem">
    <div class="ui-el-sortlist-item{x:iif(@fixed, '-fixed', '')}" id="{@id}">
        <xsl:apply-templates />
    </div>
</xsl:template>

