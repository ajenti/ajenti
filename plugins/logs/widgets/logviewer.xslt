<xsl:template match="logviewer">
    <div class="ui-el-logviewer" style="width: {x:css(@width, '200')}; height: {x:css(@height, '200')};">
        <xsl:apply-templates />
    </div>
</xsl:template>

<xsl:template match="logfilter">
    <div class="ui-el-logfilter">
        <span class="ui-el-label-1">Filter: </span>
        <input id="logfilter" class="ui-el-input" onkeyup="ui_update_log_filter()"/>
    </div>
    <script>
        logfilter_orig = null;
    </script>
</xsl:template>

