<xsl:template match="tabheader">
    <li class="ui-el-tab-header {x:iif(@active or (../@active = @id), 'active', '')}">
        <xsl:if test="../@live = 'True' or @live = 'True'">
            <xsl:attribute name="onclick">
                <xsl:if test="@form">
                    return Ajenti.submit('<xsl:value-of select="@form" />', '<xsl:value-of select="@id" />');
                </xsl:if>
                <xsl:if test="not(@form)">
                    return Ajenti.query('/handle/tab/click/<xsl:value-of select="@id" />');
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
                $('#<xsl:value-of select="@id"/>').pills();
            </xsl:if>
        </script>
    </div>
</xsl:template>




<xsl:template match="treecontainer">
    <div class="ui-el-treecontainernode">
        <a href="#" onclick="return Ajenti.UI.toggleTreeNode('{@id}');" class="text">
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
    <li class="{x:iif(@active, 'active', '')}" onclick="return Ajenti.query('/handle/listitem/click/{@id}');">
        <xsl:apply-templates />
    </li>
</xsl:template>




<xsl:template match="editable">
    <a href="#" onclick="return Ajenti.UI.editableActivate('{x:idesc(@id)}')" class="ui-el-editable-inactive" id="{x:idesc(@id)}-normal">
        <xsl:value-of select="@value" />
    </a>
    <div id="{x:idesc(@id)}" class="ui-el-editable input-append" style="display:none">
        <input id="{x:idesc(@id)}-active-url" type="hidden" name="url" value="/handle/form/submit/{@id}"/>
        <input type="text" name="value" value="{@value}" />
        <hlabel class="add-on active">
            <img href="#" src="/dl/core/ui/stock/dialog-ok.png" onclick="return Ajenti.submit('{x:idesc(@id)}', 'OK')" />
        </hlabel>
    </div>
</xsl:template>


<xsl:template match="sortlist">
    <div id="{@id}" class="ui-el-sortlist">
        <xsl:apply-templates />
    </div>
    <script>
        $('#<xsl:value-of select="@id"/>').sortable();
    </script>
</xsl:template>

<xsl:template match="sortlistitem">
    <div class="ui-el-sortlist-item{x:iif(@fixed, '-fixed', '')}" id="{@id}">
        <xsl:apply-templates />
    </div>
</xsl:template>

