class window.Controls.terminal__thumbnail extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control terminal-thumbnail">
                <img src="/terminal/#{@properties.tid}/thumbnail" />
                <a class="close">&#x2715;</a>
            </div>
        """)
        @dom.click () =>
            window.open "/terminal/#{@properties.tid}"
        @dom.find('a').click (e) =>
            @event('close')
            e.stopPropagation()


class window.Terminal
    constructor: () ->
        @id = document.location.href.split('/')[4]
        @term = $('#term')
        @socket = io.connect('/terminal')

        $(document).keypress (event) =>
            ch = @filter_key(event, $.browser.mozilla)
            if event.which != 13
                @send(JXG.Util.Base64.encode(ch))
            event.preventDefault()

        $(document).keyup (event) =>
            ch = @filter_key(event)
            @send(JXG.Util.Base64.encode(ch))
            event.preventDefault()

        @socket.on 'set', (data) =>
            @draw(data)

        @select()
        
    select: () =>
        @socket.send(JSON.stringify(type: 'select', tid: @id))

    send: (ch) =>
        @socket.send(JSON.stringify(type: 'key', key: ch, tid: @id))

    draw: (data) ->
        data = JSON.parse(JXG.decompress(data))

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
        
        @term.css(
            left: (window.innerWidth / 2 - @term.width() / 2) + 'px'
            top: (20 + window.innerHeight / 2 - @term.height() / 2) + 'px'
        )

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
            if true || bg != cell[2] || fg != cell[1] || (iidx == @cursy && i == @cursx) || (iidx == @cursy && i == @cursx+1)
                misc = '';
                sty = '';
                if iidx == @cursy && i == @cursx
                    misc = ' class="cursor" '
                if cell[3] || cell[4] || cell[5]
                    if cell[3]
                        sty += 'font-weight: bold;'
                    if cell[4]
                        sty += 'font-style: italic;'
                    if cell[5]
                        sty += 'text-decoration: underline;'
                r += '</pre><pre' + misc + ' style="color:' + cell[1] + ';background:' + cell[2] + ';' + sty + '">'
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


"""
var _cursor, _cursx, _cursy, _tid;



function termSend(data) {
    $.ajax({
        url: '/terminal/' + _tid + '/post/' + data,
        type: 'GET',
        cache: false,
        success: function () {
            termActivity();
        },
        error: termOffline
    });
}

function 


function termInit(tid) {

}






function termTV() {
    $('.tv-noise').css('width', document.width*2 + 'px');
    $('.tv-noise').css('height', document.height*2 + 'px');
    $('.tv-line').css('width', document.width*2 + 'px');
    $('.tv-noise').show();
    $('.tv-line').show();
    termTVUpdate();
    termTVUpdateLine(true);
    termTVUpdateShake();
    $('.tv-icon').fadeOut();
}

function termTVUpdate() {
    $('.tv-noise').each(function (i,e) {
        var dx = Math.floor(Math.random()*50-25), dy = Math.floor(Math.random()*50-25);
        $(e).css('top', dx+'px');
        $(e).css('left', dy+'px');
    });

    $('.tv-line').each(function (i,e) {
        $(e).css('top', e.offsetTop + 3 + "px");
    });
    
    $('#term').css('opacity', 0.9+Math.random()*0.1+"");
    setTimeout("termTVUpdate()", 50);
}

function termTVUpdateLine(force) {
    $('.tv-line').each(function (i,e) {
        if (Math.random() > 0.25 && (force || e.offsetTop > $('#term')[0].offsetTop + $('#term')[0].clientHeight))
            $(e).css('top', $('#term')[0].offsetTop-Math.random()*500);
    });
    setTimeout("termTVUpdateLine()", 3000+Math.random()*4000);
}

function termTVUpdateShake(reset) {
    $('#term div').each(function (i,e) {
        var dx = Math.floor(Math.random()*5);
        if (reset) dx = 0;
        $(e).css('padding-left', dx+'px');
    });

    if (reset)
        setTimeout("termTVUpdateShake()", Math.random()*4000);
    else
        if (Math.random() < 0.20)
            setTimeout("termTVUpdateShake(true)", 20);
        else
            setTimeout("termTVUpdateShake()", 20);
}
"""