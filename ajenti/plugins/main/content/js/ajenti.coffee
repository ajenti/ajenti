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
        @socket.on 'crash', (data) ->
            data = JSON.parse(data)
            console.log 'CRASH:', data
            ajentiCrash(data)
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

    sendUpdates: () ->
        if @updaterTimeout
            clearTimeout(@updaterTimeout)
        @updaterTimeout = setTimeout () =>
            if @pendingUpdates.length > 0
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
        
        if @properties.visible != true
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
        if not @uid
            return
        @ui.event(this, event, params)

    _int_to_px: (i) ->
        if i == null or i == 'auto'
            return 'auto'
        if parseInt(i) == NaN
            return i + ''
        return i + 'px'

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