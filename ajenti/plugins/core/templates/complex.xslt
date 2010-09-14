<xsl:template match="tabheader">
    <a href="#">
        <div class="ui-el-tab-header" id="tabheader-{@pid}-{@id}" onclick="javascript:ui_tabswitch('{@pid}','{@id}')">
            <xsl:value-of select="@text" />
        </div>
    </a>
</xsl:template>

<xsl:template match="tabheadernode">
    <tr>
        <td id="{@id}" class="ui-el-tab-header-box">
            <xsl:apply-templates />
        </td>
    </tr>
</xsl:template>

<xsl:template match="tabbody">
    <span class="ui-el-tab-body" id="tabbody-{@pid}-{@id}">
        <xsl:apply-templates />
    </span>
</xsl:template>

<xsl:template match="tabcontrol">
    <table>
        <xsl:apply-templates />
        <script>
            ui_tabswitch('<xsl:value-of select="@id"/>', '<xsl:value-of select="x:attr(@active, '0')"/>');
        </script>
    </table>
</xsl:template>




<xsl:template match="treecontainer">
    <div class="ui-el-treecontainernode">
        <a href="#">
            <div class="ui-el-treecontainernode-title" onclick="javascript:ui_showhide('{@id}');ajaxNoUpdate('/handle/treecontainer/click/{@id}');ui_treeicon('{@id}-btn');return false">
                <div class="ui-el-treecontainernode-button">
                    <img id="{@id}-btn" src="/dl/core/ui/tree-{x:iif(@expanded, 'minus', 'plus')}.png" />
                </div>
                <xsl:value-of select="@text" />
            </div>
        </a>
        <div class="ui-el-treecontainernode-inner" id="{@id}" style="{x:iif(@expanded, '', 'display:none;')}">
            <xsl:apply-templates />
        </div>
    </div>
</xsl:template>

<xsl:template match="treecontainernode">
    <div class="ui-el-treecontainernode-title">
        <div class="ui-el-treecontainernode-inner">
            <xsl:apply-templates />
        </div>
    </div>
</xsl:template>

