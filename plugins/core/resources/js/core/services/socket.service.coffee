angular.module('core').service 'socket', ($log, $location, $rootScope, $q, socketFactory, urlPrefix) ->
    @socket = socketFactory(
        ioSocket: io.connect('/socket', resource: "#{urlPrefix}/socket.io".substring(1))
    )

    @socket.on 'connecting', (e) ->
        $log.log('Connecting')

    @socket.on 'connect_failed', (e) ->
        $log.log('Connection failed', e)

    @socket.on 'reconnecting', (e) ->
        $log.log('Reconnecting')

    @socket.on 'reconnect_failed', (e) ->
        $log.log('Reconnection failed', e)

    @socket.on 'reconnect', (e) ->
        $rootScope.socketConnectionLost = false
        $log.log('Reconnected')

    @socket.on 'connect', (e) ->
        $rootScope.socketConnectionLost = false
        $rootScope.$broadcast 'socket-event:connect'
        $log.log('Connected')

    @socket.on 'disconnect', (e) ->
        $rootScope.socketConnectionLost = true
        $rootScope.$broadcast 'socket-event:disconnect'
        $log.error('Disconnect', e)

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

    @socket.on 'message', (msg) ->
        if msg[0] == '{'
            msg = JSON.parse(msg)
        $log.debug 'Socket message from', msg.plugin, msg.data
        $rootScope.$broadcast "socket:#{msg.plugin}", msg.data

    return this

