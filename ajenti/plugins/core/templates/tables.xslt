<xsl:template match="layouttable">
    <table cellspacing="0" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
        <xsl:apply-templates />
    </table>
</xsl:template>

<xsl:template match="layouttablerow">
    <tr style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
        <xsl:apply-templates />
    </tr>
</xsl:template>

<xsl:template match="layouttablecell">
    <td class="ui-el-layouttable-cell" colspan="{@colspan}" rowspan="{@rowspan}" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')}; padding-right: {x:css(@spacing, '4')}; padding-bottom: {x:css(@spacing, '4')};">
        <xsl:apply-templates />
    </td>
</xsl:template>
    

<xsl:template match="datatable">
    <table cellspacing="0" cellpadding="0" class="ui-el-table" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
        <xsl:apply-templates />
    </table>
</xsl:template>

<xsl:template match="datatablerow">
    <tr class="ui-el-table-row{x:iif(@header, '-header', '')}" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
        <xsl:apply-templates />
    </tr>
</xsl:template>

<xsl:template match="datatablecell">
    <td class="ui-el-table-cell{x:iif(@hidden, '-hidden', '')}" colspan="{@colspan}" rowspan="{@rowspan}" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')}; padding-right: {x:css(@spacing, '4')}; padding-bottom: {x:css(@spacing, '4')};">
        <xsl:apply-templates />
    </td>
</xsl:template>

