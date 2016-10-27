angular.module('core').config($routeProvider =>
    $routeProvider.when('/view/settings', {
        templateUrl: '/settings:resources/partial/index.html',
        controller: 'SettingsIndexController'
    })
);
