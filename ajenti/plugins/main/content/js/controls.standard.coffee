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
        return $('<div></div>').append(child.dom)


class window.Controls.vc extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container vc"></div>
        """)
        @childContainer = @dom

    wrapChild: (child) ->
        return $('<div></div>').append(child.dom)


class window.Controls.label extends window.Control
    createDom: () ->
        @dom = $("""<span class="control label">#{@properties.text}</span>""")


class window.Controls.icon extends window.Control
    createDom: () ->
        icon = _make_icon(@properties.icon)
        @dom = $("""<div class="control icon style-#{@properties.style}">#{icon}</div>""")


class window.Controls.button extends window.Control
    createDom: () ->
        icon = _make_icon(@properties.icon)
        @dom = $("""<a href="#" class="control button style-#{@properties.style}">#{icon}#{@properties.text}</a>""")
        @dom.click (e) =>
            @event 'click'
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

    goEditMode: () =>
        @label.hide()
        @input.show()
        @input.focus()

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
                    type="checkbox" 
                    #{if @properties.value then 'checked="checked"' else ''} 
                />
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


class window.Controls.combobox extends window.Control
    createDom: () ->
        @dom = $("""
            <div><input class="control combobox" type="text" value="#{@properties.value}" /></div>
        """)
        @input = @dom.find('input')
        @data = []
        for i in [0..@properties.items.length]
            do (i) =>
                @data.push {label: @properties.items[i], value: @properties.values[i]}
        @input.autocomplete source: @data

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
            @event 'click'
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
        @dom = $("""<table cellspacing="0" cellpadding="0" class="control table" style="width: #{w}"></table>""")
        @childContainer = @dom#.find('>tbody')

    wrapChild: (child) ->
        return child.dom


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
                <td colspan="999" class="control collapserow">
                    <div class="header"></div>
                    <div class="children"></div>
                </td>
            </tr>
        """)
        @container = @dom.find('.children')
        @header = @dom.find('.header')
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
                e.preventDefault()
            selected: @active
        })

    wrapChild: (child) ->
        return $("""<div data-index="#{@children.length-1}" id="#{child.uid}"></div>""").append(child.dom)