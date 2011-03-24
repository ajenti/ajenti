<xsl:template match="servicepluginpanel">
    <toolbar>
        <div class="ui-el-servicepluginpanel">
        <xsl:choose>
            <xsl:when test="@status = 'running'">
                <img src="/dl/core/ui/stock/status-running.png" style="padding-top: 2px;"/>
                <label text="{@servicename}"/>
                <toolseparator /><toolbutton class="servicecontrol" text="Restart" id="restart" /><toolbutton class="servicecontrol" text="Stop" id="stop"/>
            </xsl:when>
            <xsl:when test="@status = 'stopped'">
                <img src="/dl/core/ui/stock/status-stopped.png" style="padding-top: 2px;"/>
                <label text="{@servicename}"/>
                <toolseparator /><toolbutton class="servicecontrol" text="Start" id="start"/>
            </xsl:when>
            <xsl:when test="@status = 'failed'">
                <img src="/dl/core/ui/stock/status-failed.png" style="padding-top: 2px;"/>
                <label text="{@servicename}"/>
                <toolseparator /><toolbutton class="servicecontrol" text="Restart" id="restart"/>
            </xsl:when>
        </xsl:choose>
        </div>
    </toolbar>
</xsl:template>
