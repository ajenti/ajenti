angular.module('ajenti.plugins').controller 'PluginsIndexController', ($scope, $http, notify, pageTitle, messagebox, core) ->
    pageTitle.set('Plugins')

    $scope.selectedInstalledPlugin = null
    $scope.selectedRepoPlugin = null
    $scope.coreUpgradeAvailable = null

    $scope.refresh = () ->
        $http.get('/api/plugins/list/installed').success (data) ->
            $scope.installedPlugins = data
            $http.get('/api/plugins/repo/list').success (data) ->
                $scope.repoList = data
                $scope.notInstalledRepoList = (x for x in $scope.repoList when !$scope.isInstalled(x))
            .error (err) ->
                notify.error 'Could not load plugin repository', err.message
        .error (err) ->
            notify.error 'Could not installed plugin list', err.message
        $http.get('/api/plugins/pypi/list').success (data) ->
            $scope.pypiList = data
        $http.get('/api/plugins/core/check-upgrade').success (data) ->
            $scope.coreUpgradeAvailable = data

    $scope.refresh()

    $scope.upgradeCore = () ->
        msg = messagebox.show progress: true, title: 'Upgrading'
        $http.get("/api/plugins/core/upgrade/#{$scope.coreUpgradeAvailable}").success () ->
            messagebox.show(title: 'Done', text: 'Upgrade complete. A panel restart is absolutely required.', positive: 'Restart now').then () ->
                core.forceRestart()
        .error (err) ->
            notify.error 'Upgrade failed', err.message
        .finally () ->
            msg.close()

    $scope.isInstalled = (plugin) ->
        if not $scope.isInstalled
            return false
        for p in $scope.installedPlugins
            if p.name == plugin.name
                return true
        return false

    $scope.getUpgrade = (plugin) ->
        if not $scope.repoList or not plugin
            return null
        for p in $scope.repoList
            if p.name == plugin.name and p.version != plugin.version
                return p
        return null

    $scope.installPlugin = (plugin) ->
        $scope.selectedRepoPlugin = null
        $scope.selectedInstalledPlugin = null
        msg = messagebox.show progress: true, title: 'Installing'
        $http.get("/api/plugins/pypi/install/#{plugin.name}/#{plugin.version}").success () ->
            $scope.refresh()
            messagebox.show(title: 'Done', text: 'Installed. A panel restart is required.', positive: 'Restart now', negative: 'Later').then () ->
                core.forceRestart()
        .error (err) ->
            notify.error 'Install failed', err.message
        .finally () ->
            msg.close()

    $scope.uninstallPlugin = (plugin) ->
        if plugin.name in ['plugins', 'settings']
            messagebox.show(title: 'Warning', text: 'This will remove the Plugins plugin. You can reinstall it later using PIP.', positive: 'Continue', negative: 'Cancel').then () ->
                doUninstallPlugin(plugin)
        else
            doUninstallPlugin(plugin)

    $scope.doUninstallPlugin = (plugin) ->
        $scope.selectedRepoPlugin = null
        $scope.selectedInstalledPlugin = null
        messagebox.show(title: 'Uninstall', text: "Uninstall #{plugin.name}?", positive: 'Uninstall', negative: 'Cancel').then () ->
            msg = messagebox.show progress: true, title: 'Uninstalling'
            $http.get("/api/plugins/pypi/uninstall/#{plugin.name}").success () ->
                $scope.refresh()
                messagebox.show(title: 'Done', text: 'Uninstalled. A panel restart is required.', positive: 'Restart now', negative: 'Later').then () ->
                    core.forceRestart()
            .error (err) ->
                notify.error 'Uninstall failed', err.message
            .finally () ->
                msg.close()

    $scope.restart = () ->
        core.restart()
