angular.module('ajenti.plugins').controller 'PluginsIndexController', ($scope, $http, notify, pageTitle, messagebox, tasks, core) ->
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

    $scope.$on 'push:plugins', ($event, msg) ->
        if msg.type == 'install-done'
            $scope.refresh()
            messagebox.show(title: 'Done', text: 'Installed. A panel restart is required.', positive: 'Restart now', negative: 'Later').then () ->
                core.forceRestart()
            $scope.installProgressMessage.close()
        if msg.type == 'install-error'
            notify.error 'Install failed', msg.error
            $scope.installProgressMessage.close()

    $scope.installPlugin = (plugin) ->
        $scope.selectedRepoPlugin = null
        $scope.selectedInstalledPlugin = null
        $scope.installProgressMessage = messagebox.show progress: true, title: 'Installing'
        tasks.start('aj.plugins.plugins.tasks.InstallPlugin', [], name: plugin.name, version: plugin.version)

    $scope.uninstallPlugin = (plugin) ->
        if plugin.name == 'plugins'
            messagebox.show(title: 'Warning', text: 'This will remove the Plugins plugin. You can reinstall it later using PIP.', positive: 'Continue', negative: 'Cancel').then () ->
                $scope.doUninstallPlugin(plugin)
        else
            $scope.doUninstallPlugin(plugin)

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
