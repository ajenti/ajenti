class window.Controls.logs__log extends window.Control
    createDom: () ->
        @dom = $("""
            <textarea class="control textbox log">
            </textarea>
        """)
        if @properties.path
            @socket = io.connect('/log')
            @socket.send(JSON.stringify(type: 'select', path: @properties.path))
            @socket.on 'add', @add

    add: (data) =>
        @dom.val(@dom.val() + data)
        @dom[0].scrollTop = @dom[0].scrollHeight;
