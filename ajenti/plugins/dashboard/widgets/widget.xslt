<xsl:template match="widget">
    <div>
        <div class="ui-el-widget-hdr">
            <xsl:value-of select="@title"/>
            <a href="#" onclick="ajax('/handle/widget/move/{@id}/up')">↑</a>
            <a href="#" onclick="ajax('/handle/widget/move/{@id}/down')">↓</a>
            <xsl:if test="@pos = 'l'">
                <a href="#" onclick="ajax('/handle/widget/move/{@id}/right')">→</a>
            </xsl:if>
            <xsl:if test="@pos = 'r'">
                <a href="#" onclick="ajax('/handle/widget/move/{@id}/left')">←</a>
            </xsl:if>
        </div>    
        <div height="{x:attr(@height, '')}" class="ui-el-widget">
            <xsl:apply-templates />
        </div>
    </div>
</xsl:template>

