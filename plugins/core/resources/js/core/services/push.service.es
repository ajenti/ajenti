angular.module('core').service('push', function($rootScope, $q, $log, $http, socket) {
    $rootScope.$on('socket:push', ($event, msg) => {
        $log.debug('Push message from', msg.plugin, msg.message);
        $rootScope.$broadcast(`push:${msg.plugin}`, msg.message);
    });

    return this;
});
