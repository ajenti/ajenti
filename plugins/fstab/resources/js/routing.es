angular.module('ajenti.fstab').config(($routeProvider) => {
    $routeProvider.when('/view/fstab', {
        templateUrl: '/fstab:resources/partial/index.html',
        controller: 'FstabIndexController',
    });
});
