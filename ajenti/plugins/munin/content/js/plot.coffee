class window.Controls.munin__plot extends window.Control
    createDom: () ->
        url = '/ajenti:munin-proxy/' + encodeURIComponent(@properties.url)
        if @properties.period
            url += @properties.period + '.png'
        @dom = $("""
            <div class="control munin-plot #{if @properties.widget then 'widget-mode' else ''}">
                <img src="#{url}" />
                <a href="#" class="control button style-normal"><i class="icon-plus"></i> Add widget</a>
            </div>
        """)
        @dom.find('a').click () =>
            @event('widget', url: @properties.url, period: @properties.period)

