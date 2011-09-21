<xsl:template match="formbox">
        <div id="{@id}" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')}; overflow: hidden">
            <input id="{@id}-url" type="hidden" name="url" value="/handle/form/submit/{@id}"/>
            <xsl:apply-templates />
            <div>
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

<xsl:template match="simpleform">
        <div id="{@id}" style="display:inline-block">
            <input id="{@id}-url" type="hidden" name="url" value="/handle/form/submit/{@id}"/>
            <xsl:apply-templates />
        </div>
</xsl:template>

<xsl:template match="dialogbox">
<div>
    <div id="{@id}-wr" class="modal-wrapper">
        <div id="{@id}" class="modal">
            <input id="{@id}-url" type="hidden" name="url" value="/handle/dialog/submit/{@id}"/>
                <div class="modal-body">
                    <xsl:apply-templates />
                </div>

                <div class="modal-footer">
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
    <script>
        $('#blackout').show();
        ui_center('<xsl:value-of select="@id"/>-wr');
        ui_scroll_top();
    </script>
</div>
</xsl:template>


<xsl:template match="inputbox">
<div>
    <div class="ui-el-modal-wrapper" id="{@id}-wr">
        <div id="{@id}">
            <input id="{@id}-url" type="hidden" name="url" value="/handle/dialog/submit/{@id}"/>
            <div class="ui-el-dialog" width="{@width}" height="{@height}">
                <div class="ui-el-dialog-content">
                    <table>
                        <tr><td><label text="{@text}"/></td></tr>
                        <tr><td><textinput size="30" password="{@password}" name="value" value="{@value}"/></td></tr>
                    </table>
                </div>
                <div class="ui-el-modal-buttons">
                    <button text="OK" onclick="form" action="OK" form="{@id}"/>
                    <button text="Cancel" onclick="form" action="Cancel" form="{@id}"/>
                </div>
            </div>
        </div>
    </div>
    <script>
        $('#blackout').show();
        ui_center('<xsl:value-of select="@id"/>-wr');
        ui_scroll_top();
        $('#<xsl:value-of select="@id"/> input[type!=hidden]')[0].focus();
    </script>
</div>
</xsl:template>



<xsl:template match="areainputbox">
<div>
    <div class="ui-el-modal-wrapper" id="{@id}-wr">
        <div id="{@id}">
            <input id="{@id}-url" type="hidden" name="url" value="/handle/dialog/submit/{@id}"/>
            <div class="ui-el-dialog">
                <div class="ui-el-dialog-content">
                    <table>
                        <tr><td><label text="{@text}"/></td></tr>
                        <tr><td><textinputarea id="{@id}-inner" name="value" nodecode="True" value="{x:b64(@value)}" width="{x:attr(@width,400)}" height="{x:attr(@height,400)}"/></td></tr>
                    </table>
                </div>
                <div class="ui-el-modal-buttons">
                    <button text="OK" onclick="form" action="OK" form="{@id}"/>
                    <button text="Cancel" onclick="form" action="Cancel" form="{@id}"/>
                </div>
            </div>
        </div>
    </div>
    <script>
        $('#blackout').show();
        ui_center('<xsl:value-of select="@id"/>-wr');
        ui_scroll_top();
        $('#<xsl:value-of select="@id"/> textarea[type!=hidden]')[0].focus();
    </script>
</div>
</xsl:template>


<xsl:template match="codeinputbox">
<div>
    <div class="ui-el-modal-wrapper" id="{@id}-wr">
        <div id="{@id}">
            <input id="{@id}-url" type="hidden" name="url" value="/handle/dialog/submit/{@id}"/>
            <div class="ui-el-dialog">
                <div class="ui-el-dialog-content">
                    <table>
                        <tr><td><label text="{@text}"/></td></tr>
                        <tr><td><codeinputarea id="{@id}-inner" name="value" nodecode="True" value="{x:b64(@value)}" width="{x:attr(@width,600)}" height="{x:attr(@height,400)}"/></td></tr>
                    </table>
                </div>
                <div class="ui-el-modal-buttons">
                    <button text="OK" onclick="form" action="OK" form="{@id}"/>
                    <button text="Cancel" onclick="form" action="Cancel" form="{@id}"/>
                </div>
            </div>
        </div>
    </div>
    <script>
        $('#blackout').show();
        ui_center('<xsl:value-of select="@id"/>-wr');
        ui_scroll_top();
    </script>
</div>
</xsl:template>
