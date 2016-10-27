angular.module('core').config($routeProvider =>
    $routeProvider.when('/view/supervisor', {
        templateUrl: '/supervisor:resources/partial/index.html',
        controller: 'SupervisorIndexController'
    })
);
