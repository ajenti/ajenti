_make_icon = (icon) ->
    if icon then """<i class="icon-#{icon}"></i>&nbsp;""" else ""



class window.Controls.default extends window.Control
    createDom: () ->
        @dom = $("""
            <div>
            </div>
        """)
        @childContainer = @dom


class window.Controls.pad extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container pad">
            </div>
        """)
        @childContainer = @dom


class window.Controls.box extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        h = @_int_to_px(@properties.height)
        @dom = $("""
            <div class="control container box" style="width: #{w}; height: #{h}; 
                overflow: #{if @properties.scroll then 'auto' else 'hidden'}">
            </div>
        """)
        @childContainer = @dom


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
            <div class="control container hc"></div>
        """)
        @childContainer = @dom

    wrapChild: (child) ->
        return $('<div></div>').append(child.dom)[0]


class window.Controls.vc extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container vc"></div>
        """)
        @childContainer = @dom

    wrapChild: (child) ->
        return $('<div></div>').append(child.dom)[0]


class window.Controls.label extends window.Control
    createDom: () ->
        @dom = $("""<span class="control label #{@properties.style}">#{@properties.text}</span>""")


class window.Controls.tooltip extends window.Control
    createDom: () ->
        @dom = $("""
            <span class="control tooltip #{@properties.style}">
                <div class="container"></div>
                <div class="tip">
                    <div></div>
                    <div>#{@properties.text}</div>
                </div>
            </span>
        """)
        @childContainer = @dom.find('.container')


class window.Controls.icon extends window.Control
    createDom: () ->
        icon = _make_icon(@properties.icon)
        @dom = $("""<div class="control icon style-#{@properties.style}">#{icon}</div>""")



class window.Controls.button extends window.Control
    createDom: () ->
        icon = _make_icon(@properties.icon)
        @dom = $("""<a href="#" class="control button style-#{@properties.style}">#{icon}#{@properties.text}</a>""")
        @dom.click (e) =>
            if not @properties.warning or confirm(@properties.warning)
                if @event 'click'
                    @cancel(e)


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


class window.Controls.textbox extends window.Control
    createDom: () ->
        @dom = $("""
            <div><input class="control textbox" type="text" value="#{@properties.value}" /></div>
        """)
        @input = @dom.find('input')

    detectUpdates: () ->
        r = {}
        value = @input.val()
        if @properties.type == 'integer'
            value = parseInt(value)
        if value != @properties.value
            r.value = value
        @properties.value = value
        return r


class window.Controls.editable extends window.Control
    createDom: () ->
        icon = _make_icon(@properties.icon)
        @dom = $("""
            <div class="control editable">
                <div class="control label">#{icon} <span>#{@properties.placeholder ? @properties.value}</span></div>
                <input class="control textbox" type="text" value="#{@properties.value}" />
            </div>
        """)
        @label = @dom.find('.label')
        @input = @dom.find('input')
        @input.hide()
        @label.click @goEditMode
        @input.blur @goViewMode
        @input.keyup (e) =>
            if e.which == 13
                @goViewMode()
            @cancel(e)

    goViewMode: () =>
        @label.find('>span').html(@properties.placeholder ? @input.val())
        @input.hide()
        @label.show()

    goEditMode: (e) =>
        @label.hide()
        @input.show()
        @input.focus()
        e.stopPropagation()
        e.preventDefault()

    detectUpdates: () ->
        r = {}
        value = @input.val()
        if @properties.type == 'integer'
            value = parseInt(value)
        if value != @properties.value
            r.value = value
        return r


class window.Controls.checkbox extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control checkbox">
                <input 
                    id="#{@properties.uid}"
                    type="checkbox" 
                    #{if @properties.value then 'checked="checked"' else ''} 
                />
                <label for="#{@properties.uid}">
                    <div class="tick"></div>
                </label>
                <div class="control label">#{@properties.text}</div>
            </div>
        """)
        @input = @dom.find('input')

    detectUpdates: () ->
        r = {}
        checked = @input.is(':checked')
        if checked != @properties.value
            r.value = checked
        @properties.value = checked
        return r


class window.Controls.dropdown extends window.Control
    createDom: () ->
        @dom = $("""
            <div><select class="control dropdown" /></div>
        """)
        @input = @dom.find('select')
        @data = []
        for i in [0...@properties.labels.length]
            do (i) =>
                @input.append("""<option value="#{@properties.values[i]}" #{if @properties.values[i] == @properties.value then 'selected' else ''}>#{@properties.labels[i]}</option>""")

        if @properties.server
            @input.change (e) =>
                @event('change', {})
                @cancel(e)

    detectUpdates: () ->
        r = {}
        value = @input.val()
        if @properties.type == 'integer'
            value = parseInt(value)
        if value != @properties.value
            r.value = value
        @properties.value = value
        return r


class window.Controls.combobox extends window.Control
    createDom: () ->
        @dom = $("""
            <div><input class="control combobox" type="text" value="#{@properties.value}" /></div>
        """)
        @input = @dom.find('input')
        @data = []
        for i in [0...@properties.labels.length]
            do (i) =>
                @data.push {label: @properties.labels[i], value: @properties.values[i]}

        if @properties.separator != null
            @input.autocomplete {
                source: (request, response) =>
                    vals = @getVals()
                    response($.ui.autocomplete.filter(@data, vals.pop()))
                focus: () =>
                    return false
                select: (event, ui) =>
                    vals = @getVals()
                    vals.pop()
                    vals.push ui.item.value
                    @input.val(vals.join(@properties.separator))
                    return false
                minLength: 0
            }
        else
            @input.autocomplete source: @data, minLength: 0
        @input.click () =>
            @input.autocomplete 'search', ''

    getVals: () ->
        return @input.val().split(@properties.separator)

    detectUpdates: () ->
        r = {}
        value = @input.val()
        if @properties.type == 'integer'
            value = parseInt(value)
        if value != @properties.value
            r.value = value
        @properties.value = value
        return r


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



class window.Controls.list extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control list">
            </div>
        """)
        @childContainer = @dom


class window.Controls.listitem extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control listitem">
            </div>
        """)
        @childContainer = @dom
        @dom.click (e) =>
            if @event 'click'
                @cancel(e)


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
        @dom = $("""<table cellspacing="0" cellpadding="0" class="control table" style="width: #{w}">
                <tbody></tbody>
            </table>""")
        @childContainer = @dom#.find('>tbody')

    wrapChild: (child) ->
        return child.dom


class window.Controls.sortabledt extends window.Controls.dt
    createDom: () ->
        super()
        @tbody = @dom.find('tbody')
        @tbody.sortable().disableSelection()
        @order = []

    detectUpdates: () ->
        @newOrder = []
        @tbody.find('>*').each (i, e) =>
            @newOrder.push parseInt($(e).attr('data-order'))

        r = {}
        if @newOrder != @order and @order.length > 0
            r.order = @newOrder

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
        @dom = $("""<td style="width: #{w}"></td>""")
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


class window.Controls.progressbar extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        pw = @_int_to_px(Math.round(@properties.width * @properties.value))
        @dom = $("""
            <div class="control progressbar" style="width: #{w}">
                <div class="fill" style="width: #{pw}"></div>
            </div>
        """)
        @childContainer = @dom
