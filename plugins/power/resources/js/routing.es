angular.module('core').config($routeProvider =>
    $routeProvider.when('/view/power', {
        templateUrl: '/power:resources/partial/index.html',
        controller: 'PowerIndexController'
    })
);
