angular.module('core').config($routeProvider => {
    $routeProvider.when('/view/datetime', {
        templateUrl: '/datetime:resources/partial/index.html',
        controller: 'DateTimeIndexController'
    })
});
