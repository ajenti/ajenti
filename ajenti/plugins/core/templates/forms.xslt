<xsl:template match="tabheadernode">
    <tr>
        <td id="{@id}" class="ui-el-tab-header-box">
            <xsl:apply-templates />
        </td>
    </tr>
</xsl:template>


<xsl:template match="formbox">
        <div id="{@id}">
            <input id="{@id}-url" type="hidden" name="url" value="/handle/form/submit/{@id}"/>
            <xsl:apply-templates />
            <div class="ui-el-modal-buttons">
            <table cellspacing="0" cellpadding="0">
                <tr>
                    <xsl:choose>
                        <xsl:when test="@hideok = 'True'" />
                        <xsl:otherwise>
                            <td><button text="OK" onclick="form" action="OK" form="{@id}"/></td>
                        </xsl:otherwise>
                    </xsl:choose>
                    <xsl:choose>
                        <xsl:when test="@hidecancel = 'True'" />
                        <xsl:otherwise>
                            <td><button text="Cancel" onclick="form" action="Cancel" form="{@id}"/></td>
                        </xsl:otherwise>
                    </xsl:choose>
                    <xsl:if test="@miscbtn">
                         <td><button text="{@miscbtn}" id="{@miscbtnid}"/></td>
                    </xsl:if>
                   </tr>
                </table>
            </div>
        </div>
</xsl:template>


<xsl:template match="errorbox">
    <div class="ui-el-error" width="{@width}" height="{@height}">
        <table>
            <tr>
                <td width="40">
                    <img src="/dl/core/ui/stock/warning.png" />
                </td>
                <td>
                    <div class="ui-el-error-title">
                        <label text="{@title}" size="3" />
                    </div>
                    <div class="ui-el-error-content">
                        <label text="{@text}" />
                    </div>
                </td>
            </tr>
        </table>
    </div>
</xsl:template>

