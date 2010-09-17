<xsl:template match="fwrule">
    <a href="#" onclick="ajax('/handle/fwrule/click/{@id}')" class="ui-el-fwrule-wr">
        <xsl:choose>
            <xsl:when test="@action = 'ACCEPT'">
                <div class="ui-el-fwrule-l-accept">ACC</div>
            </xsl:when>    
            
            <xsl:when test="@action = 'REJECT'">
                <div class="ui-el-fwrule-l-drop">REJ</div>
            </xsl:when>    

            <xsl:when test="@action = 'DROP'">
                <div class="ui-el-fwrule-l-drop">DROP</div>
            </xsl:when>    

            <xsl:when test="@action = 'LOG'">
                <div class="ui-el-fwrule-l-misc">LOG</div>
            </xsl:when>    

            <xsl:when test="@action = 'EXIT'">
                <div class="ui-el-fwrule-l-misc">EXIT</div>
            </xsl:when>    

            <xsl:when test="@action = 'MASQUERADE'">
                <div class="ui-el-fwrule-l-accept">MASQ</div>
            </xsl:when>    

            <xsl:otherwise>
                <div class="ui-el-fwrule-l-misc">RUN</div>
            </xsl:otherwise>    
        </xsl:choose>
        
        <div class="ui-el-fwrule-r-normal">
            <xsl:value-of select="@desc"/>
        </div>
    </a>
</xsl:template>


<xsl:template match="fwchain">
    <table cellspacing="0" cellpadding="0">
        <tr>
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
                                <warningminibutton text="Delete chain" id="deletechain/{@tname}/{@name}"
                                    msg="Delete rule chain {@name}"/>
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

