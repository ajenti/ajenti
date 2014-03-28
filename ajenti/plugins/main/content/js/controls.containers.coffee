class window.Controls.pad extends window.Control
    createDom: () ->
        """
            <div class="control container pad">
                <children>
            </div>
        """


class window.Controls.indent extends window.Control
    createDom: () ->
        """
            <div class="control container indent">
                <children>
            </div>
        """


class window.Controls.box extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        h = @_int_to_px(@properties.height)
        """
            <div class="control container box" style="width: #{w}; height: #{h};
                overflow: #{if @properties.scroll then 'auto' else 'hidden'}">
                <children>
            </div>
        """


class window.Controls.well extends window.Control
    createDom: () ->
        """
            <div class="control container well">
                <children>
            </div>
        """


class window.Controls.center extends window.Control
    createDom: () ->
        """
            <div class="control container center">
                <children>
            </div>
        """


class window.Controls.right extends window.Control
    createDom: () ->
        """
            <div class="control container right">
                <children>
            </div>
        """


class window.Controls.hc extends window.Control
    createDom: () ->
        """
            <table class="control container hc #{@s(@properties.style)}">
                <tr class="--child-container">
                    <children>
                </tr>
            </table>
        """

    wrapChild: (child) ->
        "<td>#{child.html}</td>"

    wrapChildLive: (child) ->
        return $('<td></td>').append(child.dom)[0]


class window.Controls.vc extends window.Control
    createDom: () ->
        """
            <div class="control container vc #{@s(@properties.style)} --child-container">
                <children>
            </div>
        """

    wrapChild: (child) ->
        "<div>#{child.html}</div>"

    wrapChildLive: (child) ->
        return $('<div></div>').append(child.dom)[0]


class window.Controls.formline extends window.Control
    createDom: () ->
        """
            <div class="control formline">
                <div class="control label">#{@s(@properties.text)}</div>
                <div>
                    <children>
                </div>
            </div>
        """


class window.Controls.formgroup extends window.Control
    createDom: () ->
        """
            <div class="control formgroup">
                <div>#{@s(@properties.text)}</div>
                <children>
            </div>
        """


class window.Controls.toolbar extends window.Control
    createDom: () ->
        """
            <div class="control container toolbar">
                <children>
            </div>
        """


class window.Controls.dt extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        """
            <table cellspacing="0" cellpadding="0" class="control table #{@s(@properties.style)} --child-container" style="width: #{w}">
                <tbody>
                    <children>
                </tbody>
            </table>
        """


class window.Controls.sortabledt extends window.Controls.dt
    setupDom: (dom) ->
        super(dom)
        @tbody = $(@dom).find('>tbody')
        @tbody.sortable(
            distance: 5
            cancel: 'input,button,a,.CodeMirror'
        )
        @order = []
        i = 1
        for child in @children
            @order.push i
            $(child.dom).attr('data-order', i)
            i += 1

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

        r.order = @newOrder
        @order = @newOrder
        return r


class window.Controls.dtr extends window.Control
    createDom: () ->
        """<tr class="--child-container"><children></tr>"""


class window.Controls.dtd extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        fw = @_int_to_px(@properties.forcewidth)
        """<td style="width: #{w}; max-width: #{fw}"><children></td>"""


class window.Controls.dth extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        """<th style="width: #{w}">#{@s(@properties.text)}<children></th>"""

    setupDom: (dom) ->
        super(dom)
        if @children.length > 0
            $(@dom).addClass('nopad')


class window.Controls.lt extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        """
            <table cellspacing="0" cellpadding="0" class="control layout-table" style="width: #{w}">
                <tbody><children></tbody>
            </table>
        """

class window.Controls.ltr extends window.Control
    createDom: () ->
        """<tr class="--child-container"><children></tr>"""


class window.Controls.ltd extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        """<td style="width: #{w}"><children></td>"""


class window.Controls.collapserow extends window.Control
    createDom: () ->
        """
            <tr>
                <td colspan="999" class="control container collapserow">
                    <div class="header"></div>
                    <div class="children"><children></div>
                </td>
            </tr>
        """

    setupDom: (dom) ->
        super(dom)
        dom_header = @dom.children[0].children[0]
        dom_children = @dom.children[0].children[1]
        dom_child_first = dom_children.children[0]

        @container = dom_children
        @expanded = @properties.expanded
        if not @properties.expanded
            @container.style.display = 'none'

        dom_header.appendChild(dom_child_first)
        @header = dom_header

        @header.addEventListener 'click', (e) =>
            @expanded = not @expanded
            #@publish()
            $(@container).toggle('blind')
            if @expanded
                @broadcast('visible')
            @cancel(e)
        , false

        return this

    detectUpdates: () ->
        r = {}
        if @expanded != @properties.expanded
            r.expanded = @expanded
        @properties.expanded = @expanded
        return r


class window.Controls.tabs extends window.Control
    createDom: () ->
        @requiresAllChildren = true

        @lastTabIndex = 0
        """
            <div class="control tabs">
                <ul></ul>
                <children>
            </div>
        """

    setupDom: (dom) ->
        super(dom)
        @active = @properties.active
        @headers = $(@dom).find('>ul')
        for child in @children
            do (child) =>
                header = $$("""<li data-index="#{child.tabIndex}"><a href="#uid-#{child.uid}">#{child.properties.title}</a></li>""")
                @headers.append(header)
        $(@dom).tabs({
            beforeActivate: (e, ui) =>
                @active = parseInt(ui.newTab.attr('data-index'))
                @event('switch', {})
                if not @properties.client
                    e.preventDefault()
            selected: @active
        })
        return this

    detectUpdates: () ->
        r = {}
        if @active != @properties.active
            r.active = @active
        @properties.active = @active
        return r

    wrapChild: (child) ->
        child.tabIndex = @lastTabIndex
        @lastTabIndex += 1
        """<div data-index="#{child.tabIndex}">#{child.html}</div>"""


class window.Controls.collapse extends window.Control
    createDom: () ->
        """
            <div class="control collapse">
                <div class="header"></div>
                <div class="children">
                    <children>
                </div>
            </div>
        """

    setupDom: (dom) ->
        super(dom)
        @header = @dom.children[0]
        @container = @dom.children[1]
        @expanded = @properties.expanded
        if not @properties.expanded
            @container.style.display = 'none'

        @header.addEventListener 'click', (e) =>
            @expanded = not @expanded
            $(@container).toggle('blind')
            if @expanded
                @broadcast('visible')
            @cancel(e)
        , false

        @header.appendChild(@container.children[0])

    detectUpdates: () ->
        r = {}
        if @expanded != @properties.expanded
            r.expanded = @expanded
        @properties.expanded = @expanded
        return r
