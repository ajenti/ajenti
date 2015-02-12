angular.module('ajenti.plugins').controller 'PluginsRepoPluginController', ($scope, $http, $routeParams, notify, pageTitle, identity) ->
    pageTitle.set('plugin.name', $scope)

    $scope.refresh = () ->
        $http.get('/api/plugins/repo/list').success (data) ->
            for p in data
                if p.name == $routeParams.id
                    $scope.plugin = p

    $scope.refresh()

