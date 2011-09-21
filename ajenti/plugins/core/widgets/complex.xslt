<xsl:template match="tabheader">
    <li id="tabheader-{@pid}-{@id}" class="ui-el-tab-header">
        <a onclick="javascript:ui_tabswitch('{@pid}','{@id}')">
            <xsl:value-of select="@text" />
        </a>
    </li>
</xsl:template>

<xsl:template match="tabheadernode">
        <ul id="{@id}" class="tabs">
            <xsl:apply-templates />
        </ul>
</xsl:template>

<xsl:template match="tabbody">
    <div id="tabbody-{@pid}-{@id}">
        <xsl:apply-templates />
    </div>
</xsl:template>

<xsl:template match="tabcontrol">
    <div>
        <xsl:apply-templates />
        <script>
            ui_tabswitch('<xsl:value-of select="@id"/>', '<xsl:value-of select="x:attr(@active, '0')"/>');
        </script>
    </div>
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


<xsl:template match="list">
    <div class="ui-el-list" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
        <table style="width: 100%">
            <xsl:apply-templates />
        </table>
    </div>
</xsl:template>

<xsl:template match="listitem">
    <tr>
        <td class="ui-el-list-item{x:iif(@active, '-active', '')}">  
            <a href="#" onclick="javascript:return ajax('/handle/listitem/click/{@id}');" style="width: 100%; display: block">
                <xsl:apply-templates />
            </a>
        </td>
    </tr>
</xsl:template>


<xsl:template match="tiles">
     <div class="ui-el-tiles" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
         <xsl:for-each select="*">
             <div style="float:left;padding: {x:css(../@spacing, '4')}">  
                 <xsl:apply-templates select="."/>
             </div>
         </xsl:for-each>    
    </div>
</xsl:template>



<xsl:template match="plugininfo">
    <div class="ui-el-plugin-info">
        <img src="{@icon}"/>
        <div>
            <label size="3" text="{@name}"/><br/>
            <outlinklabel url="{@url}" text="v{@version}, by {@author}"/>
        </div>
        <div class="description">
            <xsl:value-of select="@desc"/>
        </div>
        <div class="description">
            <xsl:apply-templates />
        </div>
    </div>
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

