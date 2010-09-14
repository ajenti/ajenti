<xsl:template match="textinput">
    <input class="ui-el-input" name="{@name}" value="{@value}" id="{@id}" size="{@size}" onkeypress="return noenter()"/>
</xsl:template>

<xsl:template match="checkbox">
    <input class="ui-el-checkbox" type="checkbox" name="{@name}" id="{@id}" checked="{x:iif(@checked, 'checked', '')}" onkeypress="return noenter()"/>
    <span class="ui-el-label-1">
        <xsl:value-of select="@text" />
    </span>
</xsl:template>

<xsl:template match="selectoption">
    <option value="{@value}" selected="{x:iif(@selected, 'selected', '')}" onkeypress="return noenter()">
        <xsl:value-of select="@text" />
    </option>
</xsl:template>

<xsl:template match="radio">
    <input class="ui-el-radio" type="radio" value="{@value}" name="{@name}" id="{@id}" checked="{x:iif(@checked, 'checked', '')}" onkeypress="return noenter()"/>
    <span class="ui-el-label-1">
        <xsl:value-of select="@text" />
    </span>
</xsl:template>

<xsl:template match="textinputarea">
    <textarea class="ui-el-textarea" name="{@name}" disabled="{x:iif(@disabled, 'disabled', '')}" style="width: {x:css(@width, '200')}; height: {x:css(@height, '200')};">
        <xsl:value-of select="@text" />
    </textarea>
</xsl:template>

