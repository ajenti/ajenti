<xsl:template match="tabheader">
    <li class="ui-el-tab-header {x:iif(@active or (../@active = @id), 'active', '')}">
        <xsl:if test="../@live = 'True' or @live = 'True'">
            <xsl:attribute name="onclick">
                <xsl:if test="@form">
                    return ajaxForm('<xsl:value-of select="@form" />', '<xsl:value-of select="@id" />');
                </xsl:if>
                <xsl:if test="not(@form)">
                    return ajax('/handle/tab/click/<xsl:value-of select="@id" />');
                </xsl:if>
            </xsl:attribute>
        </xsl:if>
        <a href="#{@id}">
            <xsl:value-of select="@text" />
        </a>
    </li>
</xsl:template>

<xsl:template match="tabbody">
    <div id="{@id}" class="{x:iif(@active or (../@active = @id), 'active', '')}">
        <xsl:apply-templates />
    </div>
</xsl:template>

<xsl:template match="tabcontrol">
    <div>
        <ul id="{@id}" class="tabs">
            <xsl:apply-templates select="./tabheader" />
        </ul>
        <div class="tab-content">
            <xsl:apply-templates select="./tabbody" />
        </div>
        <script>
            <xsl:if test="not(@live)">
                $('{@id}').tabs();
            </xsl:if>
        </script>
    </div>
</xsl:template>




<xsl:template match="treecontainer">
    <div class="ui-el-treecontainernode">
        <a href="#" onclick="return Ajenti.toggleTreeNode('{@id}');" class="text">
            <img id="{@id}-btn" src="/dl/core/ui/tree-{x:iif(@expanded, 'minus', 'plus')}.png" />
            <xsl:value-of select="@text" />
        </a>
        <div id="{@id}" style="{x:iif(@expanded, '', 'display:none;')}">
            <xsl:apply-templates />
        </div>
    </div>
</xsl:template>

<xsl:template match="treecontainernode">
    <div class="ui-el-treecontainernode {x:iif(@active, 'active', '')}">
        <xsl:apply-templates />
    </div>
</xsl:template>


<xsl:template match="list">
    <ul class="ui-el-list" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
        <xsl:apply-templates />
    </ul>
</xsl:template>

<xsl:template match="listitem">
    <li class="{x:iif(@active, 'active', '')}" onclick="javascript:return ajax('/handle/listitem/click/{@id}');">
        <xsl:apply-templates />
    </li>
</xsl:template>




<xsl:template match="editable">
    <a href="#" onclick="return ui_editable_activate('{x:idesc(@id)}')" class="ui-el-link ui-el-editable-inactive" id="{x:idesc(@id)}-normal">
        <xsl:value-of select="@value" />
    </a>
    <div class="ui-el-editable" style="display:none" id="{x:idesc(@id)}-active">
        <div id="{x:idesc(@id)}">
            <input id="{x:idesc(@id)}-active-url" type="hidden" name="url" value="/handle/form/submit/{@id}"/>
            <input type="text" name="value" value="{@value}" />
            <img href="#" src="/dl/core/ui/stock/dialog-ok.png" onclick="return ui_editable_save('{x:idesc(@id)}')" />
            <img href="#" src="/dl/core/ui/stock/dialog-cancel.png" onclick="return ui_editable_cancel('{x:idesc(@id)}')" />
        </div>
    </div>
</xsl:template>
