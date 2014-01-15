window._make_icon = (icon) ->
    if icon then """<i class="icon-#{icon}"></i>""" else ""


class window.Controls.default extends window.Control
    createDom: () ->
        """
            <div >
                <children>
            </div>
        """


class window.Controls.label extends window.Control
    createDom: () ->
        """<span class="control label #{@s(@properties.style)}">#{@s(@properties.text)}</span>"""


class window.Controls.tooltip extends window.Control
    createDom: () ->
        """
            <div class="control tooltip #{@s(@properties.style)}">
                <div class="container" title="">
                    <children>
                </div>
            </div>
        """

    setupDom: (dom) ->
        super(dom)
        $(@dom).find('.container').tooltip({
            content: () => """
                <div class="control tooltip body">
                    <div>
                        #{@s(@properties.text)}
                    </div>
                    <div>
                    </div>
                </div>
            """
            position: 
                my: "left-15 bottom"
                at: "center top"
        })


class window.Controls.icon extends window.Control
    createDom: () ->
        icon = _make_icon(@properties.icon)
        """<div class="control icon style-#{@s(@properties.style)}">#{icon}</div>"""


class window.Controls.button extends window.Control
    createDom: () ->
        icon = _make_icon(@properties.icon)
        """<a href="#" class="control button style-#{@s(@properties.style)}">#{icon} #{@s(@properties.text)}</a>"""

    setupDom: (dom) ->
        super(dom)
        @dom.addEventListener 'click', (e) =>
            if not @properties.warning or confirm(@properties.warning)
                if @event 'click'
                    @cancel(e)
        return this


class window.Controls.togglebutton extends window.Control
    createDom: () ->
        icon = _make_icon(@properties.icon)
        """<a href="#" class="control button style-#{@s(@properties.style)} #{if @properties.pressed then 'pressed' else ''}">#{icon} #{@s(@properties.text)}</a>"""

    setupDom: (dom) ->
        super(dom)
        $(@dom).click (e) =>
            if @event 'click'
                @cancel(e)


class window.Controls.list extends window.Control
    createDom: () ->
        """
            <div class="control container list --child-container">
                <children>
            </div>
        """


class window.Controls.listitem extends window.Control
    createDom: () ->
        """
            <div class="control container listitem --child-container">
                <children>
            </div>
        """

    setupDom: (dom) ->
        super(dom)
        $(@dom).click (e) =>
            if @event 'click'
                @cancel(e)
        return this


class window.Controls.progressbar extends window.Control
    createDom: () ->
        w = @_int_to_px(@properties.width)
        """
            <div class="control progressbar #{@s(@properties.style)}" style="width: #{w}">
                <div class="fill">
                    <div class="tip"></div>
                </div>
            </div>
        """

    setupDom: (dom) ->
        super(dom)
        @setProgress(@properties.value)

    setProgress: (p) ->
        pw = @_int_to_px(Math.round(@properties.width * p))
        $(@dom).find('.fill').css({width: pw})
