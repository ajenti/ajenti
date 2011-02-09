<xsl:template match="formbox">
        <div id="{@id}">
            <input id="{@id}-url" type="hidden" name="url" value="/handle/form/submit/{@id}"/>
            <xsl:apply-templates />
            <div class="ui-el-modal-buttons">
                                <xsl:choose>
                                    <xsl:when test="@hideok = 'True'" />
                                    <xsl:otherwise>
                                        <button text="OK" onclick="form" action="OK" form="{@id}"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                                <xsl:choose>
                                    <xsl:when test="@hidecancel = 'True'" />
                                    <xsl:otherwise>
                                        <button text="Cancel" onclick="form" action="Cancel" form="{@id}"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                                <xsl:if test="@miscbtn">
                                     <button text="{@miscbtn}" id="{@miscbtnid}"/>
                                </xsl:if>
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
                                <xsl:choose>
                                    <xsl:when test="@hideok = 'True'" />
                                    <xsl:otherwise>
                                        <button text="OK" onclick="form" action="OK" form="{@id}"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                                <xsl:choose>
                                    <xsl:when test="@hidecancel = 'True'" />
                                    <xsl:otherwise>
                                        <button text="Cancel" onclick="form" action="Cancel" form="{@id}"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                                <xsl:if test="@miscbtn">
                                     <button text="{@miscbtn}" id="{@miscbtnid}"/>
                                </xsl:if>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script> 
        ui_fullscreen('<xsl:value-of select="@id"/>-bo'); 
        ui_center('<xsl:value-of select="@id"/>-wr'); 
        ui_scroll_top();
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
        ui_scroll_top();
    </script>
</div>
</xsl:template>



<xsl:template match="areainputbox">
<div>
    <div class="ui-el-modal-blackout" id="{@id}-bo"/>
    <div class="ui-el-modal-wrapper" id="{@id}-wr">
        <div id="{@id}">
            <input id="{@id}-url" type="hidden" name="url" value="/handle/dialog/submit/{@id}"/>
            <div class="ui-el-dialog">
                <div class="ui-el-dialog-content">
                    <table>
                        <tr><td><label text="{@text}"/></td></tr>
                        <tr><td><textinputarea id="{@id}-inner" name="value" nodecode="True" value="{x:b64(@value)}" width="{x:attr(@width,400)}" height="{x:attr(@height,400)}"/></td></tr>
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
        ui_scroll_top();
    </script>
</div>
</xsl:template>

