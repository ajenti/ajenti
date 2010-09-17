<xsl:template match="fwrule">
    <div class="ui-el-fwrule-wr">
        <xsl:if test="@action = 'ACCEPT'">
            <div class="ui-el-fwrule-l-accept">ACC</div>
        </xsl:if>    
            
        <xsl:if test="@action = 'REJECT'">
            <div class="ui-el-fwrule-l-drop">REJ</div>
        </xsl:if>    

        <xsl:if test="@action = 'DROP'">
            <div class="ui-el-fwrule-l-drop">DROP</div>
        </xsl:if>    

        <xsl:if test="@action = 'LOG'">
            <div class="ui-el-fwrule-l-misc">LOG</div>
        </xsl:if>    

        <xsl:if test="@action = 'EXIT'">
            <div class="ui-el-fwrule-l-misc">EXIT</div>
        </xsl:if>    

        <xsl:if test="@action = 'RUN'">
            <div class="ui-el-fwrule-l-misc">RUN</div>
        </xsl:if>    

        <xsl:if test="@action = 'MASQUERADE'">
            <div class="ui-el-fwrule-l-accept">MASQ</div>
        </xsl:if>    
            
        <div class="ui-el-fwrule-r-normal">
            from all
        </div>
    </div>
</xsl:template>


<xsl:template match="fwchain">
    <table cellspacing="0" cellpadding="0">
        <tr>
            <td class="ui-el-fwchain-tl">
                <xsl:value-of select="@name"/>
            </td>
            <td class="ui-el-fwchain-tr">
            </td>
        </tr>
        <tr>
            <td class="ui-el-fwchain-c" colspan="2">
                <vcontainer spacing="5">
                    <xsl:apply-templates />
                </vcontainer>
            </td>
        </tr>
    </table>
</xsl:template>

