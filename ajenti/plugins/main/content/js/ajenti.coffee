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
        return new cls(this, json, children)

    replace: (ui) ->
        @ui = ui
        $('.root').empty().append(@ui.dom)

    queueUpdate: (update) ->
        @pendingUpdates.push update

    sendUpdates: () ->
        @stream.emit_ui_update @pendingUpdates
        @pendingUpdates = []

    event: (control, event, params) ->
        update = 
            type: 'event'
            id: control.id,
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
        @_ = @properties._
        @childContainer = null
        @dom = null
        @createDom()
        for child in @children
            do (child) =>
                @append(child)

    createDom: () ->
        ""

    append: (child) ->
        @childContainer.append(child.dom)

    remove: (child) ->
        child.remove()

    event: (event, params) ->
        @ui.event(this, event, params)

