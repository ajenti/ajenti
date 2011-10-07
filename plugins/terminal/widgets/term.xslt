<xsl:template match="terminalthumbnail">
	<a href="/terminal/{@id}" target="_term_{@id}" class="terminal-thumbnail">
		<img class="thumbnail" src="/terminal-thumb/{@id}" />
		<div class="overlay" />
		<span class="closebtn" onclick="return Ajenti.query('/handle/term/kill/{@id}')">×</span>
	</a>
</xsl:template>