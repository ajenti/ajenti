angular.module('ajenti.iptables').config(($routeProvider) => {
    $routeProvider.when('/view/iptables', {
        templateUrl: '/iptables:resources/partial/index.html',
        controller: 'IptablesIndexController',
    });
});
