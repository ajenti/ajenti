angular.module('core').service('socket', function($log, $location, $rootScope, $q, socketFactory, urlPrefix) {
    this.enabled = true;

    let cfg = {
        resource: `${urlPrefix}/socket.io`.substring(1),
        'reconnection limit': 1,
        'max reconnection attempts': 999999
    };

    if (/Apple Computer/.test(navigator.vendor) && location.protocol === 'https:') {
        cfg.transports = ['jsonp-polling']; // Safari can go to hell
    }

    this.socket = socketFactory({
        ioSocket: io.connect('/socket', cfg)
    });

    this.socket.on('connecting', e => $log.log('Socket is connecting'));

    this.socket.on('connect_failed', e => $log.log('Socket is connection failed', e));

    this.socket.on('reconnecting', e => $log.log('Socket is reconnecting'));

    this.socket.on('reconnect_failed', e => $log.log('Socket reconnection failed', e));

    this.socket.on('reconnect', e => {
        $rootScope.socketConnectionLost = false;
        $log.log('Socket has reconnected');
    });

    this.socket.on('connect', e => {
        if (!this.enabled) {
            return;
        }
        $rootScope.socketConnectionLost = false;
        $rootScope.$broadcast('socket-event:connect');
        $log.log('Socket has connected');
    });

    this.socket.on('disconnect', e => {
        if (!this.enabled) {
            return;
        }
        $rootScope.socketConnectionLost = true;
        $rootScope.$broadcast('socket-event:disconnect');
        $log.error('Socket has disconnected', e);
    });

    this.socket.on('error', function(e) {
        $rootScope.socketConnectionLost = true;
        $log.error('Error', e);
    });

    this.send = (plugin, data) => {
        let q = $q.defer();
        let msg = {
            plugin,
            data
        };
        this.socket.emit('message', msg, () => q.resolve());
        return q.promise;
    };

    this.socket.on('message', msg => {
        if (!this.enabled) {
            return;
        }
        if (msg[0] === '{') {
            msg = JSON.parse(msg);
        }
        $log.debug('Socket message from', msg.plugin, msg.data);
        $rootScope.$broadcast(`socket:${msg.plugin}`, msg.data);
    });

    return this;
});
