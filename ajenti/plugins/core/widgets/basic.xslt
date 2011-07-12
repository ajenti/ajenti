<xsl:template match="label">
    <span class="ui-el-label-{x:attr(@size, '1')}" style="{x:iif(@bold, 'font-weight: bold;', '')} {x:iif(@monospace, 'font-family: monospace;', '')}">
        <xsl:value-of select="@text" />
    </span>
</xsl:template>


<xsl:template match="image">
    <img class="ui-el-image" src="{@file}" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};" />
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

<xsl:template match="toolbutton">
    <xsl:choose>
        <xsl:when test="@onclick = 'form'">
            <a href="#" onclick="javascript:return ajaxForm('{@form}', '{@action}');" class="ui-el-button ui-el-toolbutton">
                <xsl:if test="@icon">
                    <img src="{@icon}" />
                </xsl:if>
                <xsl:value-of select="@text" />
            </a>
        </xsl:when>
        <xsl:otherwise>
            <a href="#" id="{@id}" onclick="javascript:return ajax('/handle/{x:attr(@class, 'button')}/click/{@id}');" class="ui-el-button ui-el-toolbutton {x:iif(@small, 'ui-el-toolbutton-small', '')}">
                <xsl:if test="@icon">
                    <img src="{@icon}" />
                </xsl:if>
                <xsl:value-of select="@text" />
            </a>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="toolseparator"><a class="ui-el-toolbar-separator {x:iif(@small, 'ui-el-toolbar-separator-small', '')}"></a></xsl:template>

<xsl:template match="warningbutton">
    <a href="#" onclick="ui_showwarning('{@msg}', '{@id}');" class="ui-el-button">
        <xsl:value-of select="@text" />
    </a>
</xsl:template>

<xsl:template match="warningtoolbutton">
    <a href="#" onclick="ui_showwarning('{@msg}', '{@id}');" class="ui-el-button ui-el-toolbutton">
        <xsl:if test="@icon">
            <img src="{@icon}" />
        </xsl:if>
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
    <div class="ui-el-progressbar-wrapper">
        <div style="width:{@left}px" class="ui-el-progressbar-active">
            <div><div/></div>
        </div>
        <div style="width:{@right}px" class="ui-el-progressbar" />
    </div>
</xsl:template>

<xsl:template match="elementbox">
    <div class="ui-el-elementbox">
        <xsl:apply-templates />
    </div>
</xsl:template>

<xsl:template match="helpicon">
    <div class="ui-el-helpicon" onmouseover="ui_help_setup('{x:jsesc(@text)}')" onmousemove="ui_help_show(event)" onmouseout="ui_help_hide(event)">
        <img src="/dl/core/ui/help.png"/>
    </div>
</xsl:template>
