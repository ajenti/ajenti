angular.module('core').service 'socket', ($log, $location, $rootScope, $q, socketFactory, urlPrefix) ->
    @enabled = true

    @socket = socketFactory(
        ioSocket: io.connect('/socket', resource: "#{urlPrefix}/socket.io".substring(1))
    )

    @socket.on 'connecting', (e) ->
        $log.log('Socket is connecting')

    @socket.on 'connect_failed', (e) ->
        $log.log('Socket is connection failed', e)

    @socket.on 'reconnecting', (e) ->
        $log.log('Socket is reconnecting')

    @socket.on 'reconnect_failed', (e) ->
        $log.log('Socket reconnection failed', e)

    @socket.on 'reconnect', (e) ->
        $rootScope.socketConnectionLost = false
        $log.log('Socket has reconnected')

    @socket.on 'connect', (e) =>
        if not @enabled
            return
        $rootScope.socketConnectionLost = false
        $rootScope.$broadcast 'socket-event:connect'
        $log.log('Socket has connected')

    @socket.on 'disconnect', (e) =>
        if not @enabled
            return
        $rootScope.socketConnectionLost = true
        $rootScope.$broadcast 'socket-event:disconnect'
        $log.error('Socket has disconnect', e)

    @socket.on 'error', (e) ->
        $rootScope.socketConnectionLost = true
        $log.error('Error', e)

    @send = (plugin, data) ->
        q = $q.defer()
        msg = {
            plugin: plugin
            data: data
        }
        @socket.emit 'message', msg, () ->
            q.resolve()
        return q.promise

    @socket.on 'message', (msg) =>
        if not @enabled
            return
        if msg[0] == '{'
            msg = JSON.parse(msg)
        $log.debug 'Socket message from', msg.plugin, msg.data
        $rootScope.$broadcast "socket:#{msg.plugin}", msg.data

    return this

