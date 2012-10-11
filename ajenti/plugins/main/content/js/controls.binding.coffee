class window.Controls.bind__template extends window.Control
    append: (child) ->
        @dom = child.dom
        if not @properties.visible
            @dom.hide()
        @properties = child.properties
        @children.push child