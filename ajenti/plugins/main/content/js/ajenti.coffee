window.WEB_SOCKET_SWF_LOCATION = '/static/main/WebSocketMain.swf'


class Stream 
    constructor: () ->

    start: () ->
        @socket = io.connect('/stream')
        @socket.on 'ui', (ui) ->
            ui = JSON.parse(ui)
            console.log '<< ui', ui
            UI.replace(UI.inflate(ui))

    send: (message) ->
        console.log '>>', message
        @socket.send JSON.stringify(message)
    
    emit_ui_update: (updates) ->
        @send(type: 'ui_update', content: updates)


class UIManager
    constructor: (@stream) ->
        @ui = null
        @pendingUpdates = []

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
        if updates != null
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
        @stream.emit_ui_update @pendingUpdates
        @pendingUpdates = []

    event: (control, event, params) ->
        @checkForUpdates()
        
        update = 
            type: 'event'
            uid: control.uid,
            event: event,
            params: params ? null

        @queueUpdate update
        @sendUpdates()


window.Stream = new Stream()
window.Stream.start()

window.UI = new UIManager(window.Stream)


window.Controls = { }


class window.Control
    constructor: (@ui, @properties, @children) ->
        @uid = @properties.uid    
        @childContainer = null
        @childWrappers = {}
        @dom = null
        @createDom()
        for child in @children
            do (child) =>
                @append(child)

    createDom: () ->
        ""

    detectUpdates: () ->
        return {}

    wrapChild: (child) ->
        return child.dom

    extractUpdates: () ->
        updates = @detectUpdates()
        if $.isEmptyObject(updates)
            return null
        for k of updates
            do (k) =>
                @properties[k] = updates[k]
        return type: 'update', uid: @uid, properties: updates
        
    append: (child) ->
        wrapper = @wrapChild(child)
        @childWrappers[child.uid] = wrapper
        @childContainer.append(wrapper)

    remove: (child) ->
        child.remove()

    event: (event, params) ->
        @ui.event(this, event, params)

