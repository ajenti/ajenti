class window.Controls.bind__template extends window.Control
    append: (child) ->
        @dom = child.dom
        @children.push child