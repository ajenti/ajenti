angular.module('ajenti.plugins').controller 'PluginsIndexController', ($scope, $http, notify, pageTitle, messagebox, core) ->
    pageTitle.set('Plugins')

    $scope.selectedInstalledPlugin = null
    $scope.selectedRepoPlugin = null

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
        if not $scope.repoList or not plugin
            return false
        for p in $scope.repoList
            if p.name == plugin.name and p.version != plugin.version
                return true
        return false

    $scope.installPlugin = (plugin) ->
        $scope.selectedRepoPlugin = null
        $scope.selectedInstalledPlugin = null
        msg = messagebox.show progress: true, title: 'Installing'
        $http.get("/api/plugins/pypi/install/#{plugin.name}").success () ->
            $scope.refresh()
            messagebox.show(title: 'Done', text: 'Installed. A panel restart is required.', positive: 'Restart now', negative: 'Later').then () ->
                $scope.restart()
        .error (err) ->
            notify.error 'Install failed', err.message
        .finally () ->
            msg.close()

    $scope.uninstallPlugin = (plugin) ->
        $scope.selectedRepoPlugin = null
        $scope.selectedInstalledPlugin = null
        messagebox.show(title: 'Uninstall', text: "Uninstall #{plugin.name}?", positive: 'Uninstall', negative: 'Cancel').then () ->
            msg = messagebox.show progress: true, title: 'Uninstalling'
            $http.get("/api/plugins/pypi/uninstall/#{plugin.name}").success () ->
                $scope.refresh()
                messagebox.show(title: 'Done', text: 'Uninstalled. A panel restart is required.', positive: 'Restart now', negative: 'Later').then () ->
                    $scope.restart()
            .error (err) ->
                notify.error 'Uninstall failed', err.message
            .finally () ->
                msg.close()

    $scope.restart = () ->
        core.restart()
