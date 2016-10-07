angular.module('core').config($routeProvider => {
    $routeProvider.when('/view/auth-users', {
        templateUrl: '/auth_users:resources/partial/index.html',
        controller: 'AuthUsersIndexController'
    })
});
