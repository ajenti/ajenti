<xsl:template match="textinput">
    <input class="ui-el-input" name="{@name}" value="{@value}" id="{@id}" size="{@size}" onkeypress="return noenter()"/>
</xsl:template>

<xsl:template match="checkbox">
    <input class="ui-el-checkbox" type="checkbox" name="{@name}" id="{@id}" onkeypress="return noenter()">
        <xsl:if test="@checked = 'True'">
            <xsl:attribute name="checked"/>
        </xsl:if>
    </input>
    <span class="ui-el-label-1">
        <xsl:value-of select="@text" />
    </span>
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
    <input class="ui-el-radio" type="radio" value="{@value}" name="{@name}" id="{@id}" onkeypress="return noenter()">
        <xsl:if test="@checked = 'True'">
            <xsl:attribute name="checked"/>
        </xsl:if>
    </input>
    <span class="ui-el-label-1">
        <xsl:value-of select="@text" />
    </span>
</xsl:template>

<xsl:template match="textinputarea">
    <textarea class="ui-el-textarea" name="{@name}" style="width: {x:css(@width, '200')}; height: {x:css(@height, '200')};">
        <xsl:if test="@disabled = 'True'">
            <xsl:attribute name="disabled"/>
        </xsl:if>
        <xsl:value-of select="x:brdequote(@text)" />
    </textarea>
</xsl:template>

<xsl:template match="selecttextinput">
    <input class="ui-el-input" name="{@name}" value="{@value}" id="{@id}" size="{@size}" onkeypress="return noenter()" />
    <select onchange="document.getElementById('{@id}').value = this.value" id='{@id}-hints'>
        <option selected="">...</option>
        <xsl:apply-templates/>
    </select>
</xsl:template>

