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


<xsl:template match="dialogbox">
<div>
    <div class="ui-el-modal-blackout" id="{@id}-bo"/>
    <div class="ui-el-modal-wrapper" id="{@id}-wr">
        <div id="{@id}">
            <input id="{@id}-url" type="hidden" name="url" value="/handle/dialog/submit/{@id}"/>
            <div class="ui-el-dialog" width="{@width}" height="{@height}">
                <div class="ui-el-dialog-content">
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
            </div>
        </div>
    </div>
    <script> 
        ui_fullscreen('<xsl:value-of select="@id"/>-bo'); 
        ui_center('<xsl:value-of select="@id"/>-wr'); 
    </script>
</div>
</xsl:template>


<xsl:template match="inputbox">
<div>
    <div class="ui-el-modal-blackout" id="{@id}-bo"/>
    <div class="ui-el-modal-wrapper" id="{@id}-wr">
        <div id="{@id}">
            <input id="{@id}-url" type="hidden" name="url" value="/handle/dialog/submit/{@id}"/>
            <div class="ui-el-dialog" width="{@width}" height="{@height}">
                <div class="ui-el-dialog-content">
                    <table>
                        <tr><td><label text="{@text}"/></td></tr>
                        <tr><td><textinput name="value" value="{@value}"/></td></tr>
                    </table>
                    <div class="ui-el-modal-buttons">
                        <table cellspacing="0" cellpadding="0">
                            <tr>
                                 <td><button text="OK" onclick="form" action="OK" form="{@id}"/></td>
                                 <td><button text="Cancel" onclick="form" action="Cancel" form="{@id}"/></td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script> 
        ui_fullscreen('<xsl:value-of select="@id"/>-bo'); 
        ui_center('<xsl:value-of select="@id"/>-wr'); 
    </script>
</div>
</xsl:template>



<xsl:template match="areainputbox">
<div>
    <div class="ui-el-modal-blackout" id="{@id}-bo"/>
    <div class="ui-el-modal-wrapper" id="{@id}-wr">
        <div id="{@id}">
            <input id="{@id}-url" type="hidden" name="url" value="/handle/dialog/submit/{@id}"/>
            <div class="ui-el-dialog" width="{@width}" height="{@height}">
                <div class="ui-el-dialog-content">
                    <table>
                        <tr><td><label text="{@text}"/></td></tr>
                        <tr><td><textinputarea id="{@id}-inner" name="value" nodecode="True" value="{x:b64(@value)}" width="300"/></td></tr>
                    </table>
                    <div class="ui-el-modal-buttons">
                        <table cellspacing="0" cellpadding="0">
                            <tr>
                                 <td><button text="OK" onclick="form" action="OK" form="{@id}"/></td>
                                 <td><button text="Cancel" onclick="form" action="Cancel" form="{@id}"/></td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script> 
        ui_fullscreen('<xsl:value-of select="@id"/>-bo'); 
        ui_center('<xsl:value-of select="@id"/>-wr'); 
    </script>
</div>
</xsl:template>



<xsl:template match="progressbox">
    <div class="ui-el-modal-blackout" id="{@id}-wr"/>
    <div class="ui-el-modal-wrapper" id="{@id}-wr">
            <div class="ui-el-dialog" width="{@width}" height="{@height}">
                <div class="ui-el-dialog-content">
                    <vcontainer spacing="10">
                        <image file="/dl/core/ui/ajax-big.gif" />
                        <spacer height="10" />
                        <label text="{@status}" />
                    </vcontainer>
                </div>
            </div>
    </div>
    <script>
        scheduleRefresh(3000);
        ui_fullscreen('<xsl:value-of select="@id" />-bo');
        ui_center('<xsl:value-of select="@id" />-wr');
    </script>
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

