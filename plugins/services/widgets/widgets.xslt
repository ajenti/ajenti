<xsl:template match="servicepluginpanel">
    <div class="ui-el-toolbar ui-service-bar">
        <xsl:choose>
            <xsl:when test="@status = 'running'">
                <div class="ui-service-status-box">
                    <label text="Running"/>
                </div>
                <button class="servicecontrol" text="Restart" id="restart" icon="/dl/core/ui/stock/service-restart.png" /><toolbutton class="servicecontrol" text="Stop" id="stop" icon="/dl/core/ui/stock/service-stop.png" />
            </xsl:when>
            <xsl:when test="@status = 'stopped'">
                <div class="ui-service-status-box">
                    <label text="Stopped"/>
                </div>
                <button class="servicecontrol" text="Start" id="start" icon="/dl/core/ui/stock/service-run.png" />
            </xsl:when>
            <xsl:when test="@status = 'failed'">
                <div class="ui-service-status-box">
                    <img src="/dl/core/ui/stock/service-failed.png" />
                    <label text="Failed to start"/>
                </div>
                <button class="servicecontrol" text="Restart" id="restart" icon="/dl/core/ui/stock/service-restart.png"/>
            </xsl:when>
        </xsl:choose>
    </div>
</xsl:template>
