class window.Controls.munin__plot extends window.Control
    createDom: () ->
        url = '/munin-proxy/' + encodeURIComponent(@properties.url) + @properties.period + '.png'
        @dom = $("""<div class="control munin-plot"><img src="#{url}" /></div>""")

