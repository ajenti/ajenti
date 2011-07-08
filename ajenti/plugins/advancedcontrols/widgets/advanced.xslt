<xsl:template match="sortlist">
    <div id="{@id}" class="ui-el-sortlist">
        <xsl:apply-templates />
    </div>
    <script>
        ui_initSortList('<xsl:value-of select="@id"/>');
    </script>
</xsl:template>

<xsl:template match="sortlistitem">
    <div class="ui-el-sortlist-item{x:iif(@fixed, '-fixed', '')}" id="{@id}">
        <xsl:apply-templates />
    </div>
</xsl:template>


<xsl:template match="codeinputarea">
    <table><tr>
        <td>
            <textarea class="ui-el-textarea" name="{@name}" id="{@id}">
                <xsl:if test="@disabled = 'True'">
                    <xsl:attribute name="disabled"/>
                </xsl:if>
            </textarea>
            <script>
                <xsl:choose>
                    <xsl:when test="@nodecode = 'True'">
                        ui_fill_custom_html('<xsl:value-of select="@id"/>', '<xsl:value-of select="@value"/>');
                    </xsl:when>
                    <xsl:otherwise>
                        ui_fill_custom_html('<xsl:value-of select="@id"/>', '<xsl:value-of select="x:b64(@value)"/>');
                    </xsl:otherwise>
                </xsl:choose>
                var cm = CodeMirror.fromTextArea(
                    $('#<xsl:value-of select="@id"/>')[0],
                    {
                        theme: 'default',
                        lineNumbers: true,
                        enterMode: 'keep',
                        onChange: function (e) {
                            e.save();
                        }
                    }
                );
                var cms = $('.CodeMirror-scroll', cm.getWrapperElement())[0];
                cms.style.width = '<xsl:value-of select="x:css(@width, '200')"/>';
                cms.style.height = '<xsl:value-of select="x:css(@height, '200')"/>';
            </script> 
        </td>
        <td>
            <xsl:if test="@help and (@help != '')">
                <helpicon text="{@help}"/>
            </xsl:if>
        </td></tr>
    </table>
</xsl:template>
