angular.module('ajenti.plugins').controller 'PluginsIndexController', ($scope, $http, notify, pageTitle, identity) ->
    pageTitle.set('Plugins')

    $scope.refresh = () ->
        $http.get('/api/plugins/list/installed').success (data) ->
            $scope.installedPlugins = data
        .error (err) ->
            notify.error 'Could not installed plugin list', err.message
        $http.get('/api/plugins/pypi/list').success (data) ->
            $scope.pypiList = data
        $http.get('/api/plugins/repo/list').success (data) ->
            $scope.repoList = data
        .error (err) ->
            notify.error 'Could not load plugin repository', err.message

    $scope.refresh()

    $scope.isInstalled = (plugin) ->
        if not $scope.isInstalled
            return false
        for p in $scope.installedPlugins
            if p.name == plugin.name
                return true
        return false

    $scope.isUpgradeable = (plugin) ->
        if not $scope.repoList
            return false
        for p in $scope.repoList
            if p.name == plugin.name and p.version != plugin.version
                return true
        return false

    $scope.installPlugin = (plugin) ->
        notify.info 'Installing...'
        $http.get("/api/plugins/pypi/install/#{plugin.name}").success () ->
            notify.success 'Installed', 'Don\'t forget to restart Ajenti!'
            $scope.refresh()
        .error (err) ->
            notify.error 'Install failed', err.message

    $scope.uninstallPlugin = (plugin) ->
        notify.info 'Uninstalling...'
        if confirm("Uninstall #{plugin.name}?")
            $http.get("/api/plugins/pypi/uninstall/#{plugin.name}").success () ->
                notify.success 'Uninstalled', 'Don\'t forget to restart Ajenti!'
                $scope.refresh()
            .error (err) ->
                notify.error 'Uninstall failed', err.message
