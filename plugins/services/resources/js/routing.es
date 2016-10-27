angular.module('core').config(($routeProvider) => {
    $routeProvider.when('/view/services', {
        templateUrl: '/services:resources/partial/index.html',
        controller: 'ServicesIndexController'
    });

    $routeProvider.when('/view/services/:managerId', {
        templateUrl: '/services:resources/partial/index.html',
        controller: 'ServicesIndexController'
    });
});
