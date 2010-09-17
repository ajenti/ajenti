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
            <xsl:value-of select="@desc"/>
        </div>
    </div>
</xsl:template>


<xsl:template match="fwchain">
    <table cellspacing="0" cellpadding="0">
        <tr>
            <td class="ui-el-fwchain-tl-table">
                <xsl:value-of select="@tname"/>
            </td>
            <td class="ui-el-fwchain-tl">
                <xsl:value-of select="@name"/>
            </td>
            <xsl:choose>
                <xsl:when test="@default = 'ACCEPT'">
                   <td class="ui-el-fwchain-tr-accept">
                       ACCEPT
                   </td>
                </xsl:when>
                <xsl:when test="@default = 'REJECT' or @default = 'DROP'">
                   <td class="ui-el-fwchain-tr-drop">
                       <xsl:value-of select="@default"/>
                   </td>
                </xsl:when>
                <xsl:when test="@default = '-'">
                   <td class="ui-el-fwchain-tr-accept">
                   </td>
                </xsl:when>
            </xsl:choose>
        </tr>
        <tr>
            <td class="ui-el-fwchain-c" colspan="3">
                <vcontainer spacing="5">
                    <xsl:apply-templates />
                </vcontainer>
                    <hcontainer>
                        <minibutton text="Add rule" id="addrule/{@tname}/{@name}"/>
                        <minibutton text="Shuffle" id="shuffle/{@tname}/{@name}"/>
                        <xsl:choose>
                            <xsl:when test="@default = '-'">
                                <minibutton text="Delete chain" id="deletechain/{@tname}/{@name}"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <label text="Set default:"/>
                                <minibutton text="Accept" id="setdefault/{@tname}/{@name}/ACCEPT"/>
                                <minibutton text="Drop" id="setdefault/{@tname}/{@name}/DROP"/>
                                <minibutton text="Reject" id="setdefault/{@tname}/{@name}/REJECT"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </hcontainer>
            </td>
        </tr>
    </table>
</xsl:template>

