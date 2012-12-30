_make_icon = (icon) ->
    if icon then """<i class="icon-#{icon}"></i>&nbsp;""" else ""


class window.Controls.default extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container">
            </div>
        """)
        @childContainer = @dom



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


class window.Controls.list extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container list">
            </div>
        """)
        @childContainer = @dom


class window.Controls.listitem extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container listitem">
            </div>
        """)
        @childContainer = @dom
        @dom.click (e) =>
            if @event 'click'
                @cancel(e)


class window.Controls.progressbar extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        pw = @_int_to_px(Math.round(@properties.width * @properties.value))
        @dom = $("""
            <div class="control progressbar" style="width: #{w}">
                <div class="fill" style="width: #{pw}">
                    <div class="tip"></div>
                </div>
            </div>
        """)
        @childContainer = @dom
