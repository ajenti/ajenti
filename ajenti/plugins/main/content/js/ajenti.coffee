window.WEB_SOCKET_SWF_LOCATION = '/static/main/WebSocketMain.swf'


class window.Stream 
    constructor: () ->

    start: () ->
        @socket = io.connect('/stream')
        @socket.on 'ui', (ui) ->
            ui = JXG.decompress(ui)
            ui = JSON.parse(ui)
            console.log '<< ui', ui
            UI.replace(UI.inflate(ui))
        @socket.on 'update-request', () ->
            UI.checkForUpdates()
            UI.sendUpdates(true)
        @socket.on 'crash', (data) ->
            data = JSON.parse(data)
            console.log 'CRASH:', data
            ajentiCrash(data)
        @socket.on 'security-error', () ->
            console.log 'SECURITY ERROR'
            ajentiSecurityError()
        @socket.on 'notify', (data) ->
            Notificator.notify(data)

    send: (message) ->
        console.log '>>', message
        @socket.send JSON.stringify(message)
    
    emit_ui_update: (updates) ->
        @send(type: 'ui_update', content: updates)


class window.UIManager
    constructor: (@stream) ->
        @ui = null
        @pendingUpdates = []
        @updaterTimeout = null

    inflate: (json) ->
        children = []
        if json.visible == true
            for child in json.children
                do (child) =>
                    children.push @inflate(child)
        typeid = json.typeid.replace(':', '__')
        cls = Controls[typeid]
        if not cls
            cls = Controls.default
        return new cls(this, json, children)

    replace: (ui) ->
        @ui = ui
        $('.root').empty().append(@ui.dom)

    extractUpdates: (control, target) ->
        updates = control.extractUpdates()
        if updates
            target.push updates
        for child in control.children
            do (child) =>
                @extractUpdates(child, target)

    checkForUpdates: () ->
        updates = []
        @extractUpdates(@ui, updates)
        for update in updates
            do (update) =>
                @queueUpdate(update)

    queueUpdate: (update) ->
        @pendingUpdates.push update

    sendUpdates: (force) ->
        force ?= false
        if @updaterTimeout
            clearTimeout(@updaterTimeout)
        @updaterTimeout = setTimeout () =>
            if force or @pendingUpdates.length > 0
                @stream.emit_ui_update @pendingUpdates
            @pendingUpdates = []
            @updaterTimeout = null
        , 50

    event: (control, event, params) ->
        @checkForUpdates()
        
        update = 
            type: 'event'
            uid: control.uid,
            event: event,
            params: params ? null

        @queueUpdate update
        @sendUpdates()




window.Controls = { }


class window.Control
    constructor: (@ui, @properties, children) ->
        @properties ?= {}
        @properties.visible ?= true
        
        @uid = @properties.uid    
        @childContainer = null
        @childWrappers = {}
        @dom = null
        @children = []
        @createDom()
        if children
            for child in children
                do (child) =>
                    @append(child)
        
        if @properties.visible != true and @dom
            @dom.hide()

    createDom: () ->
        ""

    detectUpdates: () ->
        return {}

    wrapChild: (child) ->
        return child.dom

    extractUpdates: () ->
        updates = @detectUpdates()
        if not @uid or $.isEmptyObject(updates)
            return null
        for k of updates
            do (k) =>
                @properties[k] = updates[k]
        return type: 'update', uid: @uid, properties: updates
        
    append: (child) ->
        @children.push child
        wrapper = @wrapChild(child)
        @childWrappers[child.uid] = wrapper
        @childContainer.append(wrapper)

    remove: (child) ->
        child.remove()

    publish: () ->
        @ui.checkForUpdates()
        @ui.sendUpdates()
    
    event: (event, params) ->
        @ui.checkForUpdates()
        localHandler = this['on_' + event]
        if localHandler
            if not localHandler(params)
                return
        if not @uid or @properties.client
            return
        @ui.event(this, event, params)

    _int_to_px: (i) ->
        if /^[0-9]+$/.test(i)
            return i + 'px'
        if i == null or i == 'auto'
            return 'auto'
        return i + ''

    cancel: (event) ->
        event.preventDefault()
        event.stopPropagation()



# Crash handler
window.ajentiCrash = (info) ->
    $('#crash').fadeIn()
    $('#crash-traceback').html(info.message + "\n" + info.traceback)
    $('#crash-report textarea').val(info.report)

window.ajentiCrashResume = (info) ->
    $('#crash').fadeOut()

window.ajentiCrashShowReport = () ->
    $('#crash-traceback').toggle('blind')
    $('#crash-report').toggle('blind')
    setTimeout () =>
        $('#crash-report textarea').focus()[0].select()
    , 1000

window.ajentiSecurityError = () ->
    $('#security-error').fadeIn()

window.ajentiSecurityResume = (info) ->
    $('#security-error').fadeOut()


# Touch support

clickms = 100
lastTouchDown = -1

touchHandler = (event) ->
    touches = event.changedTouches
    first = touches[0]
    type = ""
    
    d = new Date()
    switch event.type
        when "touchstart"
            type = "mousedown"
            lastTouchDown = d.getTime()
        when "touchmove"
            type="mousemove"
            lastTouchDown = -1
        when "touchend"
            if lastTouchDown > -1 and (d.getTime() - lastTouchDown) < clickms
                lastTouchDown = -1
                type="click"
            else
                type="mouseup"
        else return

    simulatedEvent = document.createEvent("MouseEvent")
    simulatedEvent.initMouseEvent(type, true, true, window, 1,
                              first.screenX, first.screenY,
                              first.clientX, first.clientY, false,
                              false, false, false, 0, null)

    first.target.dispatchEvent(simulatedEvent)
    event.preventDefault()

document.addEventListener("touchstart", touchHandler, true)
document.addEventListener("touchmove", touchHandler, true)
document.addEventListener("touchend", touchHandler, true)
document.addEventListener("touchcancel", touchHandler, true)
