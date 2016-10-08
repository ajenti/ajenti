angular.module('core').config(function($routeProvider) {
    $routeProvider.when('/view/filemanager', {
        templateUrl: '/filemanager:resources/partial/index.html',
        controller: 'FileManagerIndexController'
    });

    $routeProvider.when('/view/filemanager/properties/:path*', {
        templateUrl: '/filemanager:resources/partial/properties.html',
        controller: 'FileManagerPropertiesController'
    });

    return $routeProvider.when('/view/filemanager/:path*', {
        templateUrl: '/filemanager:resources/partial/index.html',
        controller: 'FileManagerIndexController'
    });
});
