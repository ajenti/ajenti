window.WEB_SOCKET_SWF_LOCATION = '/static/main/WebSocketMain.swf'


class window.Stream 
    constructor: () ->

    start: () ->
        @socket = ajentiConnectSocket('/stream')

        @socket.on 'connect', () ->
            $('#connection-error').hide()

        @socket.on 'auth-error', () ->
            console.log 'Authentication lost!'
            location.reload()
            
        @socket.on 'disconnect', () ->
            $('#connection-error').show()

        @socket.on 'init', (data) ->
            data = JSON.parse(data)
            console.group 'Welcome to Ajenti'
            console.log 'version', data.version
            console.log 'running on', data.platform
            console.log 'your session:', data.session
            $('title').text(data.hostname)
            console.groupEnd()
            Feedback.configure(data.feedback, data.platform, data.version, data.edition)
            Feedback.emit('Login')

        @socket.on 'ui', (ui) ->
            console.group 'Received update'
            console.log 'Transfer size', ui.length
            profiler.start('Decompressing')
            ui = RawDeflate.inflate(RawDeflate.Base64.decode(ui))
            profiler.stop()
            console.log 'Payload size', ui.length
            ui = JSON.parse(ui)
            console.log 'JSON data:', ui

            UI.clear()
            profiler.start('UI inflating')
            ui = UI.inflate(ui)
            profiler.stop()
            profiler.start('UI replacement')
            UI.replace(ui)
            profiler.stop()
            
            console.log 'Total elements:', UI._total_elements
            console.groupEnd()
            Loading.hide()

        @socket.on 'ack', () ->
            Loading.hide()

        @socket.on 'update-request', () ->
            UI.checkForUpdates()
            UI.sendUpdates(true)
            Loading.show()

        @socket.on 'progress-message', (m) ->
            console.log '...', m
            Loading.show()
            Loading.setMessage(m)

        @socket.on 'crash', (data) ->
            data = JSON.parse(data)
            console.log 'CRASH:', data
            ajentiCrash(data)
            Loading.hide()

        @socket.on 'security-error', () ->
            console.log 'SECURITY ERROR'
            ajentiSecurityError()
            Loading.hide()

        @socket.on 'notify', (data) ->
            data = JSON.parse(data)
            Notificator.notify(data.type, data.text)

        @socket.on 'openTab', (data) ->
            data = JSON.parse(data)
            Tabs.addTab(data.url, data.title)

        @socket.on 'closeTab', (data) ->
            data = JSON.parse(data)
            Tabs.closeTab(data.url)

        @socket.on 'debug', (data) ->
            data = JSON.parse(data)
            console.group 'Profiling'
            for d of data.profiles
                console.log d, data.profiles[d]
            console.groupEnd()

        $('#connection-error').hide()

    send: (message) ->
        console.log 'Sending updates', message
        @socket.send JSON.stringify(message)
        Loading.show()
    
    emit_ui_update: (updates) ->
        @send(type: 'ui_update', content: updates)


class window.UIManager
    constructor: (@stream) ->
        @ui = null
        @pendingUpdates = []
        @updaterTimeout = null

    inflate: (json) ->
        children = []
        @_total_elements += 1
        if json.visible == true
            for child in json.children
                do (child) =>
                    children.push @inflate(child)
        typeid = json.typeid.replace(':', '__')
        cls = Controls[typeid]
        if not cls
            cls = Controls.default

        return new cls(this, json, children)

    clear: () ->
        @_total_elements = 0
        if @ui
            @ui.broadcast('destruct')
        $('.root *').unbind() 
        $.cleanData($('.root *')) 
        $('.root *').safeRemove()
        #$.cache = {} # Breaks stuff
        delete @ui
    
    replace: (ui) ->
        $('.ui-tooltip').remove()
        @ui = ui
        $('.root').append(@ui.dom)
        aoConnector.reportHeight($('body')[0].scrollHeight)

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

    restoreTheme: () ->
        if getCookie('ajenti-theme') == 'dark'
            @toggleTheme()

    toggleTheme: () ->
        $('html').toggleClass('ui-dark')
        $('html').toggleClass('ui-light')
        
        if $('html').hasClass('ui-dark')
            setCookie('ajenti-theme', 'dark')
        else
            setCookie('ajenti-theme', 'light')


class window.LoadingDim 
    constructor: (@dom) ->
        @dom.show()

    hide: () ->
        @setMessage('')
        $('.hide-when-loaded').hide()
        $('body').removeClass('loading')
        @dom.stop().fadeTo(125, 0, () => @dom.hide())

    show: () ->
        $('body').addClass('loading')
        @dom.show().stop().fadeTo(500, 1)

    setMessage: (m) ->
        @dom.find('.message').text(m)


class TabManager
    constructor: () ->
        @mainTab = $('#tab-ajenti')
        @tabHeadersDom = $('#tab-headers')
        @tabsDom = $('#tabs')
        @tabHeadersDom.find('a').click () =>
            @goHome()
        @goHome()
        @openTabs = {}

    goHome: () ->
        @tabsDom.find('>*').hide()
        @mainTab.show()
        @tabHeadersDom.find('a').removeClass('active')
        @tabHeadersDom.find('a:first').addClass('active')

    addTab: (url, title) ->
        if @openTabs[url]
            @openTabs[url].click()
            return
        dom = $("""
            <div class="tab"><iframe src="#{url}" /></div>
        """)
        @tabsDom.append(dom)
        headerDom = $("""
            <a href="#">#{title}<span class="close"><i class="icon-remove"></span></a></a>
        """)
        @tabHeadersDom.append(headerDom)
        @openTabs[url] = headerDom
        @openTabs[url].dom = dom
        headerDom.click () =>
            @tabsDom.find('>*').hide()
            dom.show()
            setTimeout () =>
                dom.find('iframe')[0].contentWindow.focus()
            , 100
            @tabHeadersDom.find('a').removeClass('active')
            headerDom.addClass('active')
        headerDom.find('.close').click () =>
            @closeTab(url)
        headerDom.click()

    closeTab: (url) ->
        @openTabs[url].dom.remove()
        @openTabs[url].remove()
        delete @openTabs[url]
        @goHome()

$ () ->
    window.Loading = new LoadingDim($('#loading'))
    window.Tabs = new TabManager()
    if window.UI
        UI.restoreTheme()
        $('#ui-theme-toggle').click () -> UI.toggleTheme()


window.Controls = { }


class window.Control
    constructor: (@ui, @properties, children) ->
        @properties ?= {}
        @properties.visible ?= true
        
        @uid = @properties.uid    
        @childContainer = null
        @dom = null
        @children = []
        @changed = false

        profiler.start('Generating DOM')
        @createDom()
        profiler.stop()

        if children
            for child in children
                do (child) =>
                    @append(child)
        
        if @dom and @dom.length
            @dom = @dom[0]
        if @properties.visible != true and @dom
            @dom.style.display = 'none'
        if @childContainer and @childContainer.length
            @childContainer = @childContainer[0]

    createDom: () ->
        ""

    destruct: () ->

    detectUpdates: () ->
        return {}

    markChanged: () ->
        if not @changed
            $(@dom).before("""
                <div class="changed-badge">
                    <span title="Not saved yet">*</span>
                </div>
            """)
        @changed = true
        $(@dom).addClass('changed')

    wrapChild: (child) ->
        return child.dom

    onBroadcast: (msg) ->

    broadcast: (msg) ->
        @onBroadcast(msg)
        for c in @children
            do (c) =>
                c.broadcast(msg)
        
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
        if wrapper and wrapper.length
            wrapper = wrapper[0]
        if wrapper
            if not @childContainer
                notcc = 1
            if @childContainer.length
                @childContainer = @childContainer[0]
            @childContainer.appendChild(wrapper)

    publish: () ->
        @ui.checkForUpdates()
        @ui.sendUpdates()
    
    event: (event, params) ->
        @ui.checkForUpdates()
        localHandler = this['on_' + event]
        if localHandler
            if not localHandler(params)
                return false
        if not @uid or @properties.client
            return false
        @ui.event(this, event, params)
        return true

    _int_to_px: (i) ->
        if /^[0-9]+$/.test(i)
            return i + 'px'
        if i == null or i == 'auto'
            return 'auto'
        return i + ''

    cancel: (event) ->
        event.preventDefault()
        event.stopPropagation()



#---------------------
# Crash handler
#---------------------

_escape = (s) -> s.replace(/</g, '&lt;')

window.ajentiConnectSocket = (uri) ->
    return io.connect(uri, resource: 'ajenti:socket')

window.ajentiCrash = (info) ->
    $('#crash').fadeIn()
    $('#crash-traceback').html(_escape(info.message + "\n" + info.traceback))
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



$.fn.safeRemove = () ->
    this.each (i,e) ->
        if e.parentNode
            e.parentNode.removeChild(e)



#---------------------
# SSL alert
#---------------------

$ () ->
    if location.protocol == 'https:' or location.hostname == 'localhost'
        $('#ssl-alert').hide()


#---------------------
# Detect tablets
#---------------------

if /Android|webOS|iPad|IEMobile/i.test(navigator.userAgent)
    $ () ->
        $('html').addClass('mode-tablet')
        FastClick.attach(document.body)

#---------------------
# Fast DOM
#---------------------
window.$$ = (html, container) ->
    container ?= 'div'
    div = document.createElement(container)
    div.innerHTML = html
    return div.childNodes[0]

