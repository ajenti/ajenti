class window.Controls.dashboard__dash extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container dashboard-dash">
                <div class="container widget-container container-0" data-index="0">
                </div>
                <div class="container widget-container container-1" data-index="1">
                </div>
                <div class="container trash">
                    > Dispose used widgets here <
                </div>
            </div>
        """)
        @dom.find('.container').sortable({
            connectWith: '.dashboard-dash .container'
            handle: '.handle'
            revert: 200
            placeholder: 'placeholder'
            tolerance: 'pointer'
            start: () =>
                $(@dom).find('.trash').show()
            stop: () =>
                r = {}
                $(@dom).find('.trash').hide()
                $(@dom).find('.trash .control').remove()
                $(@dom).find('>.widget-container').each (i, c) =>
                    index = parseInt($(c).attr('data-index'))
                    r[index] = []
                    $(c).find('>*').each (i, e) =>
                        r[index].push(parseInt($(e).attr('data-uid')))
                @event('reorder', indexes: r)
        }).disableSelection()

    append: (child) ->
        @dom.find(".container-#{child.properties.container}").append(child.dom)
        @children.push child


class window.Controls.dashboard__widget extends window.Control
    createDom: () ->
        @dom = $("""
            <div data-uid="#{@properties.uid}" class="control dashboard-widget">
                <div class="handle"></div>
                <div class="content"></div>
            </div>
        """)
        @childContainer = @dom.find('.content')

