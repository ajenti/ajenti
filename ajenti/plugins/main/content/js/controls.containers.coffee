class window.Controls.pad extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container pad">
            </div>
        """)
        @childContainer = @dom


class window.Controls.indent extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container indent">
            </div>
        """)
        @childContainer = @dom


class window.Controls.box extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        h = @_int_to_px(@properties.height)
        @dom = $("""
            <div class="control container box" style="width: #{w}; height: #{h}; 
                overflow: #{if @properties.scroll then 'auto' else 'visible'}">
            </div>
        """)
        @childContainer = @dom


class window.Controls.well extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container well">
            </div>
        """)
        @childContainer = @dom


class window.Controls.center extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container center">
                <div></div>
            </div>
        """)
        @childContainer = @dom.find('div')


class window.Controls.right extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container right">
            </div>
        """)
        @childContainer = @dom


class window.Controls.hc extends window.Control
    createDom: () ->
        @dom = $("""
            <table class="control container hc"><tr></tr></table>
        """)
        @childContainer = @dom.find('tr')

    wrapChild: (child) ->
        return $('<td></td>').append(child.dom)[0]


class window.Controls.vc extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container vc"></div>
        """)
        @childContainer = @dom

    wrapChild: (child) ->
        return $('<div></div>').append(child.dom)[0]


class window.Controls.formline extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control formline">
                <div class="control label">#{@properties.text}</div>
                <div class="--child-container">
                </div>
            </div>
        """)
        @childContainer = @dom.find('.--child-container')


class window.Controls.formgroup extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control formgroup">
                <div>#{@properties.text}</div>
                <div class="--child-container">
                </div>
            </div>
        """)
        @childContainer = @dom.find('.--child-container')


class window.Controls.toolbar extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container toolbar">
            </div>
        """)
        @childContainer = @dom


class window.Controls.dt extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        @dom = $("""<table cellspacing="0" cellpadding="0" class="control table #{@properties.style}" style="width: #{w}">
                <tbody></tbody>
            </table>""")
        @childContainer = @dom#.find('>tbody')

    wrapChild: (child) ->
        return child.dom


class window.Controls.sortabledt extends window.Controls.dt
    createDom: () ->
        super()
        @tbody = @dom.find('tbody')
        @tbody.sortable(
            distance: 5
            cancel: 'input,button,a'
        )
        @order = []

    detectUpdates: () ->
        @newOrder = []
        hasChanges = false
        @tbody.find('>*').each (i, e) =>
            idx = parseInt($(e).attr('data-order'))
            if (i+1) != idx
                hasChanges = true
            @newOrder.push idx

        r = {}
        if !hasChanges
            return r

        for i in [0..@order.length]
            if @newOrder[i] != @order[i]
                #console.log @newOrder , @order
                r.order = @newOrder
                break

        @order = @newOrder
        return r

    wrapChild: (child) ->
        $(child.dom).attr('data-order', @children.length)
        return child.dom

    append: (child) ->
        super(child)
        @order.push @children.length


class window.Controls.dtr extends window.Control
    createDom: () ->
        @dom = $("""<tr></tr>""")
        @childContainer = @dom

    wrapChild: (child) ->
        return child.dom


class window.Controls.dtd extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        fw = @_int_to_px(@properties.forcewidth)
        @dom = $("""<td style="width: #{w}; max-width: #{fw}"></td>""")
        @childContainer = @dom

    wrapChild: (child) ->
        return child.dom


class window.Controls.dth extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        @dom = $("""<th style="width: #{w}">#{@properties.text}</th>""")
        @childContainer = @dom

    wrapChild: (child) ->
        return child.dom


class window.Controls.lt extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        @dom = $("""<table cellspacing="0" cellpadding="0" class="control layout-table" style="width: #{w}">
                <tbody></tbody>
            </table>""")
        @childContainer = @dom#.find('>tbody')

    wrapChild: (child) ->
        return child.dom


class window.Controls.ltr extends window.Control
    createDom: () ->
        @dom = $("""<tr></tr>""")
        @childContainer = @dom

    wrapChild: (child) ->
        return child.dom


class window.Controls.ltd extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        @dom = $("""<td style="width: #{w}"></td>""")
        @childContainer = @dom

    wrapChild: (child) ->
        return child.dom


class window.Controls.collapserow extends window.Control
    createDom: () ->
        @dom = $("""
            <tr>
                <td colspan="999" class="control container collapserow">
                    <div class="header"></div>
                    <div class="children"></div>
                </td>
            </tr>
        """)
        @container = @dom.find('.children')[0]
        @header = @dom.find('.header')[0]
        @hasHeader = false
        @expanded = @properties.expanded
        if not @properties.expanded
            $(@container).hide()

        $(@header).click (e) =>
            @expanded = not @expanded
            @publish()
            $(@container).toggle('blind')
            if @expanded
                @broadcast('visible')
            @cancel(e)

    detectUpdates: () ->
        r = {}
        if @expanded != @properties.expanded
            r.expanded = @expanded
        @properties.expanded = @expanded
        return r

    append: (child) ->
        if @hasHeader
            $(@container).append(child.dom)
        else
            $(@header).append(child.dom)
            @hasHeader = true
        @children.push child


class window.Controls.tabs extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control tabs">
                <ul></ul>
            </div>
        """)
        @childContainer = @dom
        @active = @properties.active
        @headers = @dom.find('ul')
        @dom.tabs()

    detectUpdates: () ->
        r = {}
        if @active != @properties.active
            r.active = @active
        @properties.active = @active
        return r

    append: (child) ->
        super(child)
        header = $("""<li><a href="##{child.uid}">#{child.properties.title}</a></li>""")
        @headers.append(header)
        @dom.tabs('destroy')
        @dom.tabs({
            beforeActivate: (e, ui) =>
                @active = parseInt $(ui.newPanel).attr('data-index')
                @event('switch', {})
                if not @properties.client
                    e.preventDefault()
            selected: @active
        })

    wrapChild: (child) ->
        return $("""<div data-index="#{@children.length-1}" id="#{child.uid}"></div>""").append(child.dom)[0]


class window.Controls.collapse extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control collapse">
                <div class="header"></div>
                <div class="children"></div>
            </div>
        """)
        @container = @dom.find('>.children')
        @header = @dom.find('>.header')
        @hasHeader = false
        @expanded = @properties.expanded
        if not @properties.expanded
            @container.hide()

        @header.click (e) =>
            @expanded = not @expanded
            @publish()
            @container.toggle('blind')
            if @expanded
                @broadcast('visible')
            @cancel(e)

    detectUpdates: () ->
        r = {}
        if @expanded != @properties.expanded
            r.expanded = @expanded
        @properties.expanded = @expanded
        return r

    append: (child) ->
        if @hasHeader
            @container.append(child.dom)
        else
            @header.append(child.dom)
            @hasHeader = true
        @children.push child

