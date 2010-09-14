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


