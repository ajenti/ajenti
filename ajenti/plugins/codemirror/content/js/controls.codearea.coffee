class window.Controls.codearea extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control control-inset codearea"> 
            </div>
        """)
        @cm = CodeMirror @dom[0],
            value: @properties.value
            mode: @properties.mode
            lineNumbers: true
            matchBrackets: true
        @dom.find('>*').css(
            width:  @_int_to_px(@properties.width)
        )
        @dom.find('.CodeMirror-scroll').css(
            height: @_int_to_px(@properties.height)
        )

        setTimeout @cm.refresh, 1

    onBroadcast: (msg) ->
        if msg == 'visible'
            setTimeout @cm.refresh, 1

    detectUpdates: () ->
        r = {}
        value = @cm.getValue()
        if value != @properties.value
            r.value = value
        return r



