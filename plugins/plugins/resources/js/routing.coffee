angular.module('core').config ($routeProvider) ->
    $routeProvider.when '/view/plugins',
        templateUrl: '/plugins:resources/partial/index.html'
        controller: 'PluginsIndexController'
