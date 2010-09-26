<xsl:template match="servicepluginpanel">
    <div class="ui-el-pluginpanel">
        <div class="ui-el-pluginpanel-head">
            <hcontainer spacing="0">
                <image file="{@icon}"/>
                <vcontainer spacing="0">
                    <label text="{@title}" size="5" />
                    <div style="padding-left: 3px;">
                        <label text="Service: {@servicename}"/>
                    </div>
                </vcontainer>
            </hcontainer>
        </div>
        <xsl:choose>
            <xsl:when test="@status = 'running'">
                <div class="ui-el-servicepluginpanel-controls">
                    <hcontainer>
                        <img src="/dl/services/run.png" style="padding-top: 2px;"/>
                        <label text="Running"/>
                        <spacer width="10"/>
                        <minibutton class="servicecontrol" text="Restart" id="restart" />
                        <minibutton class="servicecontrol" text="Stop" id="stop"/>
                    </hcontainer>
                </div>
            </xsl:when>
            <xsl:when test="@status = 'stopped'">
                <div class="ui-el-servicepluginpanel-controls">
                    <hcontainer>
                        <img src="/dl/services/stop.png" style="padding-top: 2px;"/>
                        <label text="Stopped"/>
                        <spacer width="10"/>
                        <minibutton class="servicecontrol" text="Start" id="start"/>
                    </hcontainer>
                </div>
            </xsl:when>
            <xsl:when test="@status = 'failed'">
                <div class="ui-el-servicepluginpanel-controls">
                    <hcontainer>
                        <img src="/dl/services/fail.png" style="padding-top: 2px;"/>
                        <label text="Failed"/>
                        <spacer width="10"/>
                        <minibutton class="servicecontrol" text="Restart" id="restart"/>
                    </hcontainer>
                </div>
            </xsl:when>
        </xsl:choose>
        <div class="ui-el-pluginpanel-content">
            <xsl:apply-templates />
        </div>
    </div>
</xsl:template>
