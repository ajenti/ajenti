colors =
    normal:
        black:      '#073642'
        white:      '#eee8d5'
        green:      '#859900'
        brown:      '#af8700'
        red:        '#dc322f'
        magenta:    '#d33682'
        violet:     '#6c71c4'
        blue:       '#268bd2'
        cyan:       '#2aa198'
    bright:
        black:      '#074a5c'
        white:      '#f6f2e6'
        green:      '#bbd320'
        brown:      '#efbc10'
        red:        '#e5423f'
        magenta:    '#dd458f'
        violet:     '#7a7fd0'
        blue:       '#3198e1'
        cyan:       '#2abbb0'


angular.module('ajenti.terminal').directive 'terminal', ($timeout, $log, $q, socket, notify, terminals, hotkeys) ->
    return {
        scope: {
            id: '=?'
            onReady: '&?'
            textData: '=?'
        }
        template: '''
            <div>
                <canvas></canvas>
                <div class="paste-area" ng:class="{focus: pasteAreaFocused}">
                    <i class="fa fa-paste"></i>
                    <span ng:show="pasteAreaFocused">
                        Paste now
                    </span>

                    <textarea
                        ng:model="pasteData"
                        ng:focus="pasteAreaFocused = true"
                        ng:blur="pasteAreaFocused = false"
                    ></textarea>
                </div>

                <textarea
                    class="mobile-input-area"
                    ng:if="isMobile"
                    autocomplete="off" 
                    autocorrect="off" 
                    autocapitalize="off" 
                    spellcheck="false"
                ></textarea>

                <a class="extra-keyboard-toggle btn btn-default" ng:click="extraKeyboardVisible=!extraKeyboardVisible" ng:show="isMobile">
                    <i class="fa fa-keyboard-o"></i>
                </a>

                <div class="extra-keyboard" ng:show="extraKeyboardVisible">
                    <a class="btn btn-default" ng:click="extraKeyboardCtrl = true" ng:class="{active: extraKeyboardCtrl}">
                        Ctrl
                    </a>
                    <a class="btn btn-default" ng:click="fakeKeyEvent(38)">
                        <i class="fa fa-arrow-up"></i>
                    </a>
                    <a class="btn btn-default" ng:click="fakeKeyEvent(40)">
                        <i class="fa fa-arrow-down"></i>
                    </a>
                    <a class="btn btn-default" ng:click="fakeKeyEvent(37)">
                        <i class="fa fa-arrow-left"></i>
                    </a>
                    <a class="btn btn-default" ng:click="fakeKeyEvent(39)">
                        <i class="fa fa-arrow-right"></i>
                    </a>
                </div>
            </div>
        '''
        link: ($scope, element, attrs) ->
            element.addClass('block-element')

            $scope.isMobile = new MobileDetect(window.navigator.userAgent).mobile()
            $scope.extraKeyboardVisible = false

            $scope.charWidth = 7
            $scope.charHeight = 14
            $scope.canvas = element.find('canvas')[0]
            $scope.context = $scope.canvas.getContext('2d')
            $scope.font = '12px monospace'
            $scope.ready = false
            $scope.textLines = []
            $scope.pasteData = null

            $scope.clear = () ->
                $scope.dataWidth = 0
                $scope.dataHeight = 0

            $scope.fullReload = () ->
                q = $q.defer()
                terminals.full($scope.id).then (data) ->
                    if not data
                        q.reject()
                        return

                    socket.send 'terminal', {
                        action: 'subscribe'
                        id: $scope.id
                    }

                    $scope.clear()
                    $scope.draw(data)

                    if not $scope.ready
                        $scope.ready = true
                        $scope.onReady()
                        $timeout () -> # reflow
                            $scope.autoResize()
                    q.resolve()
                return q.promise

            $scope.clear()
            $scope.fullReload().catch () ->
                $scope.disabled = true
                $scope.onReady()
                notify.info 'Terminal was closed'

            $scope.scheduleResize = (w, h) ->
                $timeout.cancel($scope.resizeTimeout)
                $scope.resizeTimeout = $timeout () ->
                    $scope.resize(w, h)
                , 1000

            $scope.resize = (w, h) ->
                socket.send 'terminal', {
                    action: 'resize'
                    id: $scope.id
                    width: w
                    height: h
                }
                $scope.canvas.width = $scope.charWidth * w
                $scope.canvas.height = $scope.charHeight * h
                $scope.fullReload()

            $scope.autoResize = () ->
                availableWidth = element.parent().width() - 40
                availableHeight = $(window).height() - 60 - 40
                cols = Math.floor(availableWidth / $scope.charWidth)
                rows = Math.floor(availableHeight / $scope.charHeight)
                $scope.scheduleResize(cols, rows)

            $scope.$on 'window:resize', () ->
                $scope.autoResize()

            $scope.$on 'navigation:toggle', () ->
                $timeout () -> # reflow
                    $scope.autoResize()

            $scope.$on 'widescreen:toggle', () ->
                $timeout () -> # reflow
                    $scope.autoResize()

            $scope.$on 'terminal:paste', () ->
                element.find('textarea').focus()

            $scope.$on 'socket:terminal', ($event, data) ->
                if data.id != $scope.id or $scope.disabled
                    return
                if data.type == 'closed'
                    $scope.disabled = true
                    notify.info 'Terminal was closed'
                if data.type == 'data'
                    $scope.draw(data.data)

            $scope.draw = (data) ->
                #console.log 'Payload', data

                if $scope.dataWidth != data.w or $scope.dataHeight != data.h
                    $scope.dataWidth = data.w
                    $scope.dataHeight = data.h

                $scope.cursor = data.cursor
                if data.cursor
                    $scope.cursx = data.cx
                    $scope.cursy = data.cy
                else
                    $scope.cursx = -1

                $scope.context.font = $scope.font
                $scope.context.textBaseline = 'top'

                for y of data.lines
                    row = data.lines[y]
                    line = ''
                    for x in [0...row.length]
                        cell = row[x]
                        if cell
                            line += cell[0]
                    $scope.textLines[parseInt(y)] = line

                $scope.textData = $scope.textLines.join('\n')

                lns = element.find('div')
                for y of data.lines
                    row = data.lines[y]
                    y = parseInt(y)

                    $scope.context.fillStyle = colors.normal.black
                    $scope.context.fillRect(0, $scope.charHeight * y, $scope.charWidth * $scope.dataWidth, $scope.charHeight)

                    for x in [0...row.length]
                        cell = row[x]

                        if not cell
                            continue

                        defaultFG = 'white'
                        defaultBG = 'black'

                        if cell[7] # reverse
                            t = cell[1]
                            cell[1] = cell[2]
                            cell[2] = t
                            defaultFG = 'black'
                            defaultBG = 'white'

                        if cell[3]
                            $scope.context.font = 'bold ' + $scope.context.font
                        if cell[4]
                            $scope.context.font = 'italic ' + $scope.context.font

                        if cell[2]
                            if cell[2] != 'default' or cell[7]
                                $scope.context.fillStyle = colors.normal[cell[2]] or colors.normal[defaultBG]
                                $scope.context.fillRect(
                                    $scope.charWidth * x,
                                    $scope.charHeight * y,
                                    $scope.charWidth,
                                    $scope.charHeight,
                                )

                        if y == $scope.cursy and x == $scope.cursx
                            $scope.context.fillStyle = colors.normal['white']
                            $scope.context.fillRect(
                                $scope.charWidth * x,
                                $scope.charHeight * y,
                                $scope.charWidth,
                                $scope.charHeight,
                            )

                        if cell[1]
                            colorMap = if cell[3] then colors.bright else colors.normal
                            $scope.context.fillStyle = colorMap[cell[1]] or colorMap[defaultFG]
                            $scope.context.fillText(cell[0], $scope.charWidth * x, $scope.charHeight * y)
                            if cell[5]
                                $scope.context.fillRect(
                                    $scope.charWidth * x,
                                    $scope.charHeight * (y + 1) - 1,
                                    $scope.charWidth,
                                    1,
                                )

                        if cell[3] or cell[4]
                            $scope.context.font = $scope.font

            $scope.parseKey = (event, event_name, ign_arrows) ->
                ch = null

                if event.ctrlKey and event.keyCode == 17 # ctrl-V
                    return

                if event.ctrlKey and event.keyCode > 64
                    return String.fromCharCode(event.keyCode - 64)

                #$log.log event

                if event_name == 'keypress' and (event.charCode or event.which)
                    ch = String.fromCharCode(event.which)
                    if ch == '\r'
                        ch = '\n'
                    return ch

                if event_name == 'keydown' and event.keyCode >= 112 and event.keyCode <= 123
                    fNumber = event.keyCode - 111
                    switch fNumber
                        when 1
                            ch = '\x1bOP'
                        when 2
                            ch = '\x1bOQ'
                        when 3
                            ch = '\x1bOR'
                        when 4
                            ch = '\x1bOS'
                        else
                            ch = "\x1b[#{fNumber + 10}~"
                    return ch

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

                if ch
                    return ch

                return null

            $scope.sendInput = (data) ->
                socket.send 'terminal', {
                    action: 'input'
                    id: $scope.id
                    data: data
                }

            handler = (key, event, mode) ->
                if $scope.pasteAreaFocused or $scope.disabled
                    return
                if $scope.extraKeyboardCtrl
                    event.ctrlKey = true
                    $scope.extraKeyboardCtrl = false
                ch = $scope.parseKey(event, mode)
                if not ch
                    return false
                $scope.sendInput(ch)
                return true

            hotkeys.on $scope, (k, e) ->
                return handler(k, e, 'keypress')
            , 'keypress:global'

            hotkeys.on $scope, (k, e) ->
                return handler(k, e, 'keydown')
            , 'keydown:global'

            $scope.fakeKeyEvent = (code) ->
                handler(null, {keyCode: code}, 'keydown')

            $scope.$watch 'pasteData', () ->
                if $scope.pasteData
                    $scope.sendInput($scope.pasteData)
                $scope.pasteData = ''
                element.find('textarea').blur()
    }
