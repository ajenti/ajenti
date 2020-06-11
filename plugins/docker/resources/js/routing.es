angular.module('ajenti.docker').config(($routeProvider) => {
    $routeProvider.when('/view/docker', {
        templateUrl: '/docker:resources/partial/index.html',
        controller: 'DockerIndexController',
    });
});
