angular.module('core').config($routeProvider => {
    $routeProvider.when('/view/network', {
        templateUrl: '/network:resources/partial/index.html',
        controller: 'NetworkIndexController'
    })
});
