angular.module('core').service 'socket', ($log, $location, $rootScope, $q, socketFactory, urlPrefix) ->
    @socket = socketFactory(
        ioSocket: io.connect('/socket', resource: "#{urlPrefix}/socket.io".substring(1))
    )

    @socket.on 'connect', (e) ->
        $rootScope.socketConnectionLost = false
        $log.log('Connect', e)
    @socket.on 'disconnect', (e) ->
        $rootScope.socketConnectionLost = true
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
        #$log.debug('Socket message', msg)
        data = msg['data']
        $rootScope.$broadcast "socket:#{msg['plugin']}", data

    return this

