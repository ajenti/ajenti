angular.module('ajenti.hosts').config(($routeProvider) => {
    $routeProvider.when('/view/hosts', {
        templateUrl: '/hosts:resources/partial/index.html',
        controller: 'HostsIndexController',
    });
});
