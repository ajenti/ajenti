angular.module('core').config ($routeProvider) ->
    $routeProvider.when '/view/services',
        templateUrl: '/services:resources/partial/index.html'
        controller: 'ServicesIndexController'
