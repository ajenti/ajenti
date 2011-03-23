<xsl:template match="textinput">
        <input class="ui-el-input" name="{@name}" value="{@value}" id="{@id}" size="{@size}" onkeypress="return noenter()"/>
            <xsl:if test="@help and (@help != '')">
                <helpicon text="{@help}"/>
            </xsl:if>
</xsl:template>

<xsl:template match="checkbox">
    <table><tr><td>
            <input class="ui-el-checkbox" type="checkbox" name="{@name}" id="{@id}" onkeypress="return noenter()">
                <xsl:if test="@checked = 'True'">
                    <xsl:attribute name="checked"/>
                </xsl:if>
            </input>
            <span class="ui-el-label-1">
                <xsl:value-of select="@text" />
            </span>
        </td>
        <td>
            <xsl:if test="@help and (@help != '')">
                <helpicon text="{@help}"/>
            </xsl:if>
        </td></tr>
    </table>
</xsl:template>

<xsl:template match="selectoption">
    <option value="{@value}" onkeypress="return noenter()">
        <xsl:if test="@selected = 'True'">
            <xsl:attribute name="selected"/>
        </xsl:if>
        <xsl:value-of select="@text" />
    </option>
</xsl:template>

<xsl:template match="radio">
    <table><tr><td>
            <input class="ui-el-radio" type="radio" value="{@value}" name="{@name}" id="{@id}" onkeypress="return noenter()">
                <xsl:if test="@checked = 'True'">
                    <xsl:attribute name="checked"/>
                </xsl:if>
            </input>
            <span class="ui-el-label-1">
                <xsl:value-of select="@text" />
            </span>
        </td>
        <td>
            <xsl:if test="@help and (@help != '')">
                <helpicon text="{@help}"/>
            </xsl:if>
        </td></tr>
    </table>
</xsl:template>

<xsl:template match="textinputarea">
    <table><tr>
        <td>
            <textarea class="ui-el-textarea" name="{@name}" style="width: {x:css(@width, '200')}; height: {x:css(@height, '200')};" id="{@id}">
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
            </script> 
        </td>
        <td>
            <xsl:if test="@help and (@help != '')">
                <helpicon text="{@help}"/>
            </xsl:if>
        </td></tr>
    </table>
</xsl:template>

<xsl:template match="selecttextinput">
    <input class="ui-el-input" name="{@name}" value="{@value}" id="{@id}" size="{@size}" onkeypress="return noenter()" />
    <select onchange="document.getElementById('{@id}').value = this.value" id='{@id}-hints'>
        <option selected="">...</option>
        <xsl:apply-templates/>
    </select>
</xsl:template>

<xsl:template match="uploader">
    <form action="{@url}" method="POST" enctype="multipart/form-data">
        <input type="file" name="file"/>
        <input type="submit" class="ui-el-button" value="{x:attr(@text, 'Upload')}"/>
    </form>
</xsl:template>
