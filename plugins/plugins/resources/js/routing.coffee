angular.module('core').config ($routeProvider) ->
    $routeProvider.when '/view/plugins',
        templateUrl: '/plugins:resources/partial/index.html'
        controller: 'PluginsIndexController'

    $routeProvider.when '/view/plugins/installed/:id',
        templateUrl: '/plugins:resources/partial/installed-plugin.html'
        controller: 'PluginsInstalledPluginController'

    $routeProvider.when '/view/plugins/repo/:id',
        templateUrl: '/plugins:resources/partial/repo-plugin.html'
        controller: 'PluginsRepoPluginController'
