<xsl:template match="label">
    <span class="ui-el-label-{x:attr(@size, '1')}" style="{x:iif(@bold, 'font-weight: bold;', '')}">
        <xsl:value-of select="@text" />
    </span>
</xsl:template>


<xsl:template match="image">
    <img class="ui-el-image" src="{@file}" />
</xsl:template>


<xsl:template match="button">
    <a href="#" onclick="javascript:return ajax('/handle/button/click/{@id}');">
        <div class="ui-el-button">
            <xsl:value-of select="@text" />
        </div>
    </a>
</xsl:template>

<xsl:template match="progressbar">
    <table cellspacing="0" cellpadding="0">
        <tr>
            <td style="width:{@left}px" class="ui-el-progressbar-active"/>
            <td style="width:{@right}px" class="ui-el-progressbar"/></tr>
    </table>
</xsl:template>

<xsl:template match="elementbox">
    <div class="ui-el-elementbox">
        <xsl:apply-templates />
    </div>
</xsl:template>

