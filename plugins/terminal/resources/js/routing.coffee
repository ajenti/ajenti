angular.module('core').config ($routeProvider) ->
    $routeProvider.when '/view/terminal',
        templateUrl: '/terminal:resources/partial/index.html'
        controller: 'TerminalIndexController'

    $routeProvider.when '/view/terminal/:id',
        templateUrl: '/terminal:resources/partial/view.html'
        controller: 'TerminalViewController'
