angular.module('core').config($routeProvider => {
    $routeProvider.when('/view/packages/:managerId', {
        templateUrl: '/packages:resources/partial/index.html',
        controller: 'PackagesIndexController'
    })
});
