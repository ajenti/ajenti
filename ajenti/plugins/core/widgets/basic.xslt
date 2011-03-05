<xsl:template match="label">
    <span class="ui-el-label-{x:attr(@size, '1')}" style="{x:iif(@bold, 'font-weight: bold;', '')}">
        <xsl:value-of select="@text" />
    </span>
</xsl:template>


<xsl:template match="image">
    <img class="ui-el-image" src="{@file}" />
</xsl:template>


<xsl:template match="button">
    <xsl:choose>
        <xsl:when test="@onclick = 'form'">
            <a href="#" onclick="javascript:return ajaxForm('{@form}', '{@action}');" class="ui-el-button">
                <xsl:value-of select="@text" />
            </a>
        </xsl:when>
        <xsl:otherwise>
            <a href="#" id="{@id}" onclick="javascript:return ajax('/handle/{x:attr(@class, 'button')}/click/{@id}');" class="ui-el-button">
                <xsl:value-of select="@text" />
            </a>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="pluginbutton">
    <xsl:choose>
        <xsl:when test="@onclick = 'form'">
            <a href="#" onclick="javascript:return ajaxForm('{@form}', '{@action}');" class="ui-el-button ui-el-pluginbutton">
                <xsl:value-of select="@text" />
            </a>
        </xsl:when>
        <xsl:otherwise>
            <a href="#" id="{@id}" onclick="javascript:return ajax('/handle/{x:attr(@class, 'button')}/click/{@id}');" class="ui-el-button ui-el-pluginbutton">
                <xsl:value-of select="@text" />
            </a>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="warningbutton">
    <a href="#" onclick="ui_showwarning('{@msg}', '{@id}');" class="ui-el-button">
        <xsl:value-of select="@text" />
    </a>
</xsl:template>

<xsl:template match="minibutton">
    <xsl:choose>
        <xsl:when test="@onclick = 'form'">
            <a href="#" onclick="javascript:return ajaxForm('{@form}', '{@action}');" class="ui-el-minibutton">
                <xsl:value-of select="@text" />
            </a>
        </xsl:when>
        <xsl:otherwise>
            <a href="#" onclick="javascript:return ajax('/handle/{x:attr(@class, 'minibutton')}/click/{@id}');" class="ui-el-minibutton">
                <xsl:value-of select="@text" />
            </a>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="warningminibutton">
    <a href="#" onclick="ui_showwarning('{@msg}', '{@id}');" class="ui-el-minibutton">
        <xsl:value-of select="@text" />
    </a>
</xsl:template>

<xsl:template match="linklabel">
    <a href="#" onclick="javascript:return ajax('/handle/linklabel/click/{@id}');" class="ui-el-link">
        <xsl:value-of select="@text" />
    </a>
</xsl:template>

<xsl:template match="outlinklabel">
    <a href="{@url}" target="blank" class="ui-el-link">
        <xsl:value-of select="@text" />
    </a>
</xsl:template>

<xsl:template match="progressbar">
    <table cellspacing="0" cellpadding="0" class="ui-el-progressbar-wrapper">
        <tr>
            <td style="width:{@left}px" class="ui-el-progressbar-active"/>
            <td style="width:{@right}px" class="ui-el-progressbar"/>
        </tr>
    </table>
</xsl:template>

<xsl:template match="elementbox">
    <div class="ui-el-elementbox">
        <xsl:apply-templates />
    </div>
</xsl:template>

<xsl:template match="helpicon">
    <div class="ui-el-helpicon" onmouseover="ui_help_setup('{@text}')" onmousemove="ui_help_show(event)" onmouseout="ui_help_hide(event)">
        <img src="/dl/core/ui/help.png"/>
    </div>
</xsl:template>

