angular.module('ajenti.session_list').config($routeProvider => {
    $routeProvider.when('/view/session_list', {
        templateUrl: '/session_list:resources/partial/index.html',
        controller: 'SessionListIndexController'
    })
});
