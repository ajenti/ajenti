angular.module('core').config($routeProvider => {
    $routeProvider.when('/view/dashboard', {
        templateUrl: '/dashboard:resources/partial/index.html',
        controller: 'DashboardIndexController'
    });
});
