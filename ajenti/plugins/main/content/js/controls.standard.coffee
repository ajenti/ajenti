window._make_icon = (icon) ->
    if icon then """<i class="icon-#{icon}"></i>""" else ""


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
            <div class="control tooltip #{@properties.style}">
                <div class="container" title=""></div>
            </div>
        """)
        @dom.find('.container').tooltip({
            content: () => """
                <div class="control tooltip body">
                    <div>
                        #{@properties.text}
                    </div>
                    <div>
                    </div>
                </div>
            """
            position: 
                my: "left-15 bottom"
                at: "center top"
        })
        @childContainer = @dom.find('.container')


class window.Controls.icon extends window.Control
    createDom: () ->
        icon = _make_icon(@properties.icon)
        @dom = $("""<div class="control icon style-#{@properties.style}">#{icon}</div>""")



class window.Controls.button extends window.Control
    createDom: () ->
        icon = _make_icon(@properties.icon)
        @dom = $("""<a href="#" class="control button style-#{@properties.style}">#{icon} #{@properties.text}</a>""")
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
        @dom = $("""
            <div class="control progressbar #{@properties.style}" style="width: #{w}">
                <div class="fill">
                    <div class="tip"></div>
                </div>
            </div>
        """)
        @setProgress(@properties.value)
        @childContainer = @dom

    setProgress: (p) ->
        pw = @_int_to_px(Math.round(@properties.width * p))
        $(@dom).find('.fill').css({width: pw})
