<xsl:template match="label">
    <span class="ui-el-label-{x:attr(@size, '1')}" style="{x:iif(@bold, 'font-weight: bold;', '')} {x:iif(@monospace, 'font-family: monospace;', '')}">
        <xsl:value-of select="@text" />
    </span>
</xsl:template>


<xsl:template match="image">
    <img class="ui-el-image" src="{@file}" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};" />
</xsl:template>


<xsl:template match="toolbar">
    <div class="ui-el-toolbar">
        <xsl:apply-templates />
    </div>
</xsl:template>

<!-- Button magic -->
<xsl:template match="button">
    <xsl:variable name="onclickjs">
        <xsl:choose>
            <xsl:when test="@warning != ''">
                return Ajenti.showWarning('<xsl:value-of select="@warning"/>',
                    '<xsl:value-of select="@id"/>');
            </xsl:when>

            <xsl:when test="@onclick = 'form'">
                return Ajenti.submit('<xsl:value-of select="@form" />',
                    '<xsl:value-of select="@action" />');
            </xsl:when>

            <xsl:when test="@onclick = '' or not (@onclick)">
                return Ajenti.query('/handle/<xsl:value-of
                        select="x:attr(@class, 'button')" />/click/<xsl:value-of
                        select="@id" />');
            </xsl:when>

            <xsl:otherwise>
                <xsl:value-of select="@onclick" />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <xsl:variable name="design">
        <xsl:choose>
            <xsl:when test="@design != ''">
                <xsl:value-of select="@design" />
            </xsl:when>
            <xsl:otherwise>
                default
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <a href="{@href}" onclick="{$onclickjs}" class="ui-el-button btn {$design}">
        <xsl:if test="@icon">
            <img src="{@icon}" />
        </xsl:if>
        <xsl:value-of select="@text" />
    </a>
</xsl:template>

<!-- End of button magic -->



<xsl:template match="linklabel">
    <a href="#" onclick="javascript:return Ajenti.query('/handle/linklabel/click/{@id}');" class="ui-el-link" style="{x:iif(@bold, 'font-weight: bold;', '')}">
        <xsl:value-of select="@text" />
    </a>
</xsl:template>

<xsl:template match="outlinklabel">
    <a href="{@url}" target="blank" class="ui-el-link">
        <xsl:value-of select="@text" />
    </a>
</xsl:template>

<xsl:template match="progressbar">
    <div class="ui-el-progressbar-wrapper">
        <div style="width:{@left}px" class="ui-el-progressbar-active">
            <div><div/></div>
        </div>
        <div style="width:{@right}px" class="ui-el-progressbar" />
    </div>
</xsl:template>

<xsl:template match="elementbox">
    <div class="ui-el-elementbox">
        <xsl:apply-templates />
    </div>
</xsl:template>





<xsl:template match="tooltip">
    <xsl:variable name="id" select="x:id(@id)" />
    <div style="display:inline-block; {@styles}" id="{$id}">
        <xsl:apply-templates />
    </div>
    <script>
        $('#<xsl:value-of select="$id" />').twipsy({
            animate: true,
            placement: '<xsl:value-of select="x:attr(@placement, 'right')" />',
            html: true,
            live: true,
            delayIn: <xsl:value-of select="x:attr(@delay, '0')" />,
            offset: <xsl:value-of select="x:attr(@offset, '0')" />,
            title: '<xsl:value-of select="x:jsesc(x:attr(@text, ''))" />',
            trigger: '<xsl:value-of select="x:attr(@trigger, 'hover')" />',
        });
    </script>
</xsl:template>


<xsl:template match="icon">
    <tooltip placement="above" text="{@text}"><image id="{@id}" file="{@icon}"/></tooltip>
</xsl:template>

<xsl:template match="tipicon">
    <tooltip placement="above" text="{@text}"><button id="{@id}" design="tipicon" onclick="{@onclick}" warning="{@warning}" icon="{@icon}"/></tooltip>
</xsl:template>
