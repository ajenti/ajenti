class window.Controls.munin__plot extends window.Control
    createDom: () ->
        url = '/localdomain/localhost.localdomain/apache_accesses-day.png'
        url = '/munin-proxy/' + encodeURIComponent(url)
        @dom = $("""<img class="control munin-plot" src="#{url}" />""")

