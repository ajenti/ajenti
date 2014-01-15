class window.Controls.bind__template extends window.Control
    createDom: () ->
        @noUID = true
        """<children>"""

    setupDom: (dom) ->
        super(dom)
        if @children.length > 0
            @dom = @children[0].dom
            @properties = @children[0].properties