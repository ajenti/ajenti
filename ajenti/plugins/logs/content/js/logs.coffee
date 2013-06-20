class window.Controls.logs__log extends window.Control
    createDom: () ->
        @dom = $("""
            <textarea class="control textbox log">
            </textarea>
        """)
        if @properties.path
            @socket = ajentiConnectSocket('/log')
            @socket.send(JSON.stringify(type: 'select', path: @properties.path))
            @socket.on 'add', @add

    add: (data) =>
        $(@dom).val($(@dom).val() + data)
        @dom.scrollTop = @dom.scrollHeight;

    onBroadcast: (msg) ->
        if msg == 'destruct'
            if @socket
                @socket.disconnect()