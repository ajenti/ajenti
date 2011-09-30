<xsl:template match="widget">
    <div class="ui-el-widget" id="{@id}">
        <div class="handle" />
        <div class="icon">
            <xsl:if test="@icon">
                <img src="{@icon}" />
            </xsl:if>
        </div>
        <div class="title">
            <xsl:value-of select="@title"/>
        </div>

        <div class="content {@style}">
             <xsl:apply-templates />
        </div>
    </div>
</xsl:template>
