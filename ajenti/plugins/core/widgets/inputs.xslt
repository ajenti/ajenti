<xsl:template match="formline">
    <div class="clearfix">
        <hlabel for="{@iid}" text="{@text}" />
        <div class="input">
            <xsl:apply-templates />
            <xsl:if test="@help">
                <span class="help-block">
                    <xsl:value-of select="@help" />
                </span>
            </xsl:if>
        </div>
    </div>
</xsl:template>


<xsl:template match="textinput">
        <input name="{@name}" value="{@value}" id="{@id}" class="{@design}" onkeypress="return noenter()" type="{x:iif(@password, 'password', 'text')}" />
</xsl:template>

<xsl:template match="attachtextinput">
    <div class="input-prepend">
        <hlabel class="add-on {@attachmentDesign}">
            <xsl:apply-templates />
        </hlabel>
        <input name="{@name}" value="{@value}" id="{@id}" class="{@design}" onkeypress="return noenter()" type="{x:iif(@password, 'password', 'text')}" />
    </div>
</xsl:template>

<xsl:template match="checkbox">
    <div class="ui-el-checkbox">
        <input type="checkbox" name="{@name}" id="{@id}" onkeypress="return noenter()">
            <xsl:if test="@checked = 'True'">
                <xsl:attribute name="checked"/>
            </xsl:if>
        </input>
        <xsl:value-of select="@text" />
    </div>
</xsl:template>


<xsl:template match="selectinput">
    <select name="{@name}" id="{@id}" class="{@design}">
        <xsl:apply-templates />
    </select>
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
    <div class="ui-el-radio">
        <input type="radio" value="{@value}" name="{@name}" id="{@id}" onkeypress="return noenter()">
            <xsl:if test="@checked = 'True'">
                <xsl:attribute name="checked"/>
            </xsl:if>
        </input>
        <xsl:value-of select="@text" />
    </div>
</xsl:template>

<xsl:template match="textinputarea">
    <textarea class="ui-el-textarea" name="{@name}" style="width: {x:css(@width, '200')}; height: {x:css(@height, '200')};" 
        id="{@id}">
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
</xsl:template>

<xsl:template match="selecttextinput">
    <input name="{@name}" value="{@value}" id="{@id}" class="{@design}" onkeypress="return noenter()" type="text"/>
    <select onchange="$('#{@id}').val(this.value)" id='{@id}-hints' class="{@design}">
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
