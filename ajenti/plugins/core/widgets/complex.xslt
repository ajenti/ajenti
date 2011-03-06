<xsl:template match="tabheader">
    <a href="#">
        <div class="ui-el-tab-header" id="tabheader-{@pid}-{@id}" onclick="javascript:ui_tabswitch('{@pid}','{@id}')">
            <xsl:value-of select="@text" />
        </div>
    </a>
</xsl:template>

<xsl:template match="tabheadernode">
        <div id="{@id}" class="ui-el-tab-header-box">
            <xsl:apply-templates />
        </div>
</xsl:template>

<xsl:template match="tabbody">
    <div class="ui-el-tab-body" id="tabbody-{@pid}-{@id}">
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

