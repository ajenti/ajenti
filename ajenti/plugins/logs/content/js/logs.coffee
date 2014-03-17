class window.Controls.logs__log extends window.Control
    createDom: () ->
        """
            <textarea class="control textbox log">
            </textarea>
        """

    setupDom: (dom) ->
        super(dom)
        if @properties.path
            @socket = ajentiConnectSocket('/log')
            @socket.send(JSON.stringify(type: 'select', path: @properties.path))
            @socket.on 'add', @add

    add: (data) =>
        console.log 'Received: +' + data.length + ', total ' + $(@dom)[0].value.length
        $(@dom)[0].value += data
        if ($(@dom)[0].value.length > 128 * 1024)
            $(@dom)[0].value = $(@dom)[0].value.slice($(@dom)[0].value.length - 128 * 1024)
        @dom.scrollTop = @dom.scrollHeight;

    onBroadcast: (msg) ->
        if msg == 'destruct'
            if @socket
                @socket.disconnect()