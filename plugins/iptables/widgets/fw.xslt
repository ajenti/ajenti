<xsl:template match="fwrule">
    <a href="#" class="ui-el-fwrule">
        <xsl:choose>
            <xsl:when test="@id = ''" />
            <xsl:otherwise>
                <xsl:attribute name="onclick">
                    Ajenti.query('/handle/fwrule/click/<xsl:value-of select="@id"/>')
                </xsl:attribute>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:choose>
            <xsl:when test="@action = 'ACCEPT'">
                <div class="l accept">ACC</div>
            </xsl:when>

            <xsl:when test="@action = 'REJECT'">
                <div class="l drop">REJ</div>
            </xsl:when>

            <xsl:when test="@action = 'DROP'">
                <div class="l drop">DROP</div>
            </xsl:when>

            <xsl:when test="@action = 'LOG'">
                <div class="l misc">LOG</div>
            </xsl:when>

            <xsl:when test="@action = 'EXIT'">
                <div class="l misc">EXIT</div>
            </xsl:when>

            <xsl:when test="@action = 'MASQUERADE'">
                <div class="l accept">MASQ</div>
            </xsl:when>

            <xsl:otherwise>
                <div class="l misc">RUN</div>
            </xsl:otherwise>
        </xsl:choose>

        <div class="r">
            <xsl:value-of select="@desc"/>
        </div>
    </a>
</xsl:template>


<xsl:template match="fwchain">
        <div class="ui-el-fwchain">
            <div class="tl">
                <xsl:value-of select="@name"/>
            </div>
            <xsl:choose>
                <xsl:when test="@default = 'ACCEPT'">
                   <div class="tr accept">
                       ACCEPT
                   </div>
                </xsl:when>
                <xsl:when test="@default = 'REJECT' or @default = 'DROP'">
                   <div class="tr drop">
                       <xsl:value-of select="@default"/>
                   </div>
                </xsl:when>
                <xsl:when test="@default = '-'">
                   <div class="tr accept" />
                </xsl:when>
            </xsl:choose>
            <div class="c" colspan="3">
                <xsl:apply-templates />
                <br/>
                    <hcontainer>
                        <button text="Add rule" id="addrule/{@tname}/{@name}"/>
                        <button text="Shuffle" id="shuffle/{@tname}/{@name}"/>
                        <xsl:choose>
                            <xsl:when test="@default = '-'">
                                <button text="Delete chain" id="deletechain/{@tname}/{@name}"
                                    warning="Delete rule chain {@name}"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <label text="Set default:"/>
                                <button text="Accept" id="setdefault/{@tname}/{@name}/ACCEPT"/>
                                <button text="Drop" id="setdefault/{@tname}/{@name}/DROP"/>
                                <button text="Reject" id="setdefault/{@tname}/{@name}/REJECT"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </hcontainer>
            </div>
        </div>
</xsl:template>
