<xsl:template match="widget">
    <div class="ui-el-widget">
        <table><tr>
        
        <td class="ui-el-widget-icon">
            <xsl:if test="@icon">
                <img src="{@icon}" />
            </xsl:if>
        </td>
        
        <td>
            <div class="ui-el-widget-hdr">
                <span class="ui-el-widget-title {x:iif(@style='linear', 'ui-el-widget-title-linear', '')}">
                    <xsl:value-of select="@title"/>
                </span>
                <xsl:if test="@style = 'linear'">
                        <xsl:apply-templates />
                </xsl:if>
                <div class="controls">
                    <a href="#" onclick="ajax('/handle/widget/move/{@id}/delete')">⨯</a>
                    <a href="#" onclick="ajax('/handle/widget/move/{@id}/up')">↑</a>
                    <a href="#" onclick="ajax('/handle/widget/move/{@id}/down')">↓</a>
                    <xsl:if test="@pos = 'l'">
                        <a href="#" onclick="ajax('/handle/widget/move/{@id}/right')">→</a>
                    </xsl:if>
                    <xsl:if test="@pos = 'r'">
                        <a href="#" onclick="ajax('/handle/widget/move/{@id}/left')">←</a>
                    </xsl:if>
                </div>
            </div>    

            <xsl:if test="@style = 'normal'">
                <div class="ui-el-widget-content">
                    <xsl:apply-templates />
                </div>
            </xsl:if>
        </td>
        
        </tr></table>
    </div>
</xsl:template>

