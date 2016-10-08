angular.module('core').config(($routeProvider) => {
    $routeProvider.when('/view/notepad', {
        templateUrl: '/notepad:resources/partial/index.html',
        controller: 'NotepadIndexController'
    });

    $routeProvider.when('/view/notepad/:path*', {
        templateUrl: '/notepad:resources/partial/index.html',
        controller: 'NotepadIndexController'
    });
});
