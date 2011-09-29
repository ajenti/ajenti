<xsl:template match="lt">
    <table class="layout" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
        <xsl:apply-templates />
    </table>
</xsl:template>

<xsl:template match="ltr">
    <tr style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
        <xsl:apply-templates />
    </tr>
</xsl:template>

<xsl:template match="ltd">
    <td class="ui-el-layouttable-cell" colspan="{@colspan}" rowspan="{@rowspan}" style="float: {x:attr(@float, 'none')}; width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')}; padding-right: {x:css(@spacing, '7')}; padding-bottom: {x:css(@spacing, '7')};">
        <xsl:apply-templates />
    </td>
</xsl:template>


<xsl:template match="dt">
    <table cellspacing="0" cellpadding="0" class="zebra-striped" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')}; {x:iif(@noborder, 'border: none', '')}">
        <thead>
            <xsl:apply-templates select="./dtr[@header]" />
        </thead>
        <tbody>
            <xsl:apply-templates select="./dtr[not(@header)]" />
            <xsl:if test="count(./dtr[not(@header)]) = 0">
                <tr>
                    <td style="text-align:center" colspan="1000">
                        Empty
                    </td>
                </tr>
            </xsl:if>
        </tbody>
    </table>
</xsl:template>

<xsl:template match="dtr">
    <tr style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
        <xsl:apply-templates />
    </tr>
</xsl:template>

<xsl:template match="dth">
    <th colspan="{@colspan}" rowspan="{@rowspan}" class="{@design}" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
        <xsl:apply-templates />
    </th>
</xsl:template>

<xsl:template match="dtd">
    <td colspan="{@colspan}" rowspan="{@rowspan}" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
        <xsl:apply-templates />
    </td>
</xsl:template>

<xsl:template match="statuscell">
    <td class="status-cell-{@status}" colspan="{@colspan}" rowspan="{@rowspan}">
        <xsl:value-of select="@text" />
    </td>
</xsl:template>
