angular.module('ajenti.softraid').config(($routeProvider) => {
    $routeProvider.when('/view/softraid', {
        templateUrl: '/softraid:resources/partial/index.html',
        controller: 'SoftraidIndexController',
    });
});
