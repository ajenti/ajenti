<xsl:template match="servicepluginpanel">
    <toolbar>
        <div class="ui-el-servicepluginpanel">
        <xsl:choose>
            <xsl:when test="@status = 'running'">
                <img src="/dl/core/ui/stock/service-run.png" />
                <label text="{@servicename}"/>
                <toolseparator /><toolbutton class="servicecontrol" text="Restart" id="restart" icon="/dl/core/ui/stock/service-restart.png" /><toolbutton class="servicecontrol" text="Stop" id="stop" icon="/dl/core/ui/stock/service-stop.png" />
            </xsl:when>
            <xsl:when test="@status = 'stopped'">
                <img src="/dl/core/ui/stock/service-stop.png" />
                <label text="{@servicename}"/>
                <toolseparator /><toolbutton class="servicecontrol" text="Start" id="start" icon="/dl/core/ui/stock/service-run.png" />
            </xsl:when>
            <xsl:when test="@status = 'failed'">
                <img src="/dl/core/ui/stock/service-failed.png" />
                <label text="{@servicename}"/>
                <toolseparator /><toolbutton class="servicecontrol" text="Restart" id="restart" icon="/dl/core/ui/stock/service-restart.png"/>
            </xsl:when>
        </xsl:choose>
        </div>
    </toolbar>
</xsl:template>
