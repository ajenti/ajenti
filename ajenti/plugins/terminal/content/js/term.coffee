class window.Controls.terminal__thumbnail extends window.Control
    createDom: () ->
        """
            <div class="control terminal-thumbnail">
                <img src="/ajenti:terminal/#{@properties.tid}/thumbnail" />
                <a class="close">&#x2715;</a>
            </div>
        """

    setupDom: (dom) ->
        super(dom)
        $(@dom).click () =>
            Tabs.addTab "/ajenti:terminal/#{@properties.tid}", "Terminal #{@properties.tid}"
        $(@dom).find('a').click (e) =>
            @event('close')
            e.stopPropagation()



colors = 
    black: '#073642'
    green: '#859900'
    white: '#eee8d5'
    yellow: '#b58900'
    red: '#dc322f'
    magenta: '#d33682'
    violet: '#6c71c4'
    blue: '#268bd2'
    cyan: '#2aa198'


class window.Terminal
    constructor: () ->
        @id = document.location.href.split('/')[4]
        @term = $('#term')
        @socket = ajentiConnectSocket('/terminal')

        $(document).keypress (event) =>
            ch = @filter_key(event, $.browser.mozilla)
            if event.which != 13 && event.which != 8
                @send(RawDeflate.Base64.encode(ch))
            event.preventDefault()

        $(document).keyup (event) =>
            ch = @filter_key(event)
            @send(RawDeflate.Base64.encode(ch))
            event.preventDefault()

        @socket.on 'connect', () ->
            console.log 'Terminal connected'

        @socket.on 'set', (data) =>
            Loading.hide()
            @draw(data)
            @socket.send(JSON.stringify(type: 'read'))

        @socket.on 're-select', (data) =>
            @select()
        
    select: () =>
        @socket.send(JSON.stringify(type: 'select', tid: @id))

    send: (ch) =>
        if ch
            @socket.send(JSON.stringify(type: 'key', key: ch, tid: @id))

    draw: (data) ->
        data = RawDeflate.inflate(RawDeflate.Base64.decode(data))
        console.log 'Payload size', data.length
        data = JSON.parse(data)
        console.log 'Payload', data

        $('#term pre.cursor').removeClass('cursor');

        @cursor = data.cursor
        if data.cursor
            @cursx = data.cx
            @cursy = data.cy
        else
            @cursx = -1

        lns = $('#term div')
        for k of data.lines
            do (k) =>
                if lns.length <= k
                    $('#term').append(@row(data.lines[k], k))
                else
                    ln = $(lns[k])
                    ln.html(@cells(data.lines[k], k))

    row: (row, idx) ->
        '<div>' + @cells(row, idx) + '</div>';

    cells: (row, idx) ->
        r = '<pre>'
        fg = 0
        bg = 0
        bold = 0
        it = 0
        und = 0

        for i in [0...row.length]
            cell = row[i]
            iidx = parseInt(idx)
            #if i == 0 || bg != cell[2] || fg != cell[1] || (iidx == @cursy && i == @cursx) || (iidx == @cursy && i == @cursx+1)
            if true
                misc = '';
                sty = '';
                if iidx == @cursy && i == @cursx
                    misc = ' class="cursor" '
                if cell[3] || cell[4] || cell[5]
                    # bold fonts in Firefox on Linux are TOTALLY BROKEN
                    #if cell[3]
                    #    sty += 'font-weight: bold;'
                    if cell[4]
                        sty += 'font-style: italic;'
                    if cell[5]
                        sty += 'text-decoration: underline;'

                color = cell[1]
                if color == 'default'
                    color = 'white'
                color = colors[color]
                color ?= cell[1]

                background = cell[2]
                if background == 'default'
                    background = 'black'
                background = colors[background]
                background ?= cell[2]

                r += '</pre><pre' + misc + ' style="color:' + color + ';background:' + background + ';' + sty + '">'
                fg = cell[1]
                bg = cell[2]
                bold = cell[3]
                it = cell[4]
                und = cell[5]
            ch = cell[0]
            if ch == '<'
                ch = '&lt'
            if ch == '>'
                ch = '&gt'
            r += cell[0]
        r += '</pre>'
        return r


    filter_key: (event, ign_arrows) ->
        ch = event.charCode
        if event.ctrlKey
            ch = String.fromCharCode(event.keyCode - 64)
            return ch;

        if !ch && event.keyCode >= 112 && event.keyCode <= 123
            ch = '\x1b' + (event.keyCode - 111)
            return ch

        if ch 
            if event.ctrlKey
                ch = String.fromCharCode(ch - 96)
            else 
                ch = String.fromCharCode(ch)
                if ch == '\r'
                    ch = '\n'
        else
            switch event.keyCode
                when 8
                    ch = '\b'
                when 9
                    if !ign_arrows
                        ch = '\t'
                when 13,10
                    ch = '\r'
                when 38
                    if !ign_arrows
                        ch = '\x1b[A'
                when 40
                    if !ign_arrows
                        ch = '\x1b[B'
                when 39
                    if !ign_arrows
                        ch = '\x1b[C'
                when 37
                    if !ign_arrows
                        ch = '\x1b[D'
                when 46
                    ch = '\x1b[3~'
                when 35 # END
                    ch = '\x1b[F'
                when 36 # HOME
                    ch = '\x1b[H'
                when 34 #PGUP
                    ch = '\x1b[6~'
                when 33 #PGDN
                    ch = '\x1b[5~'
                when 27
                    ch = '\x1b'
                else
                    return ''
        event.preventDefault()
        return ch
