angular.module('ajenti.plugins').controller 'PluginsIndexController', ($scope, $q, $http, notify, pageTitle, messagebox, tasks, core) ->
    pageTitle.set('Plugins')

    $scope.officialKeyFingerprint = '425E 018E 2394 4B4B 4281  4EE0 BDC3 FBAA 5302 9759'
    $scope.selectedInstalledPlugin = null
    $scope.selectedRepoPlugin = null
    $scope.coreUpgradeAvailable = null

    $scope.selectRepoPlugin = (plugin) ->
        $scope.selectedRepoPlugin = plugin


    $scope.refresh = () ->
        $http.get('/api/plugins/list/installed').success (data) ->
            $scope.installedPlugins = data
            $scope.repoList = null
            $scope.repoListOfficial = null
            $scope.repoListCommunity = null
            $http.get('/api/plugins/repo/list').success (data) ->
                $scope.repoList = data
                $scope.notInstalledRepoList = (x for x in $scope.repoList when !$scope.isInstalled(x))
                $scope.repoListOfficial = (x for x in $scope.repoList when x.signature == $scope.officialKeyFingerprint)
                $scope.repoListCommunity = (x for x in $scope.repoList when x.signature != $scope.officialKeyFingerprint)
            .error (err) ->
                notify.error 'Could not load plugin repository', err.message
        .error (err) ->
            notify.error 'Could not installed plugin list', err.message
        $http.get('/api/plugins/core/check-upgrade').success (data) ->
            $scope.coreUpgradeAvailable = data

        $scope.pypiList = null
        $http.get('/api/plugins/pypi/list').success (data) ->
            $scope.pypiList = data

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

    $scope.isUninstallable = (plugin) ->
        return $scope.pypiList and $scope.pypiList[plugin.name] and plugin.name != 'core'

    $scope.isAnythingUpgradeable = () ->
        if not $scope.installedPlugins
            return false
        if $scope.coreUpgradeAvailable
            return true
        for p in $scope.installedPlugins
            if $scope.getUpgrade(p)
                return true
        return false

    $scope.upgradeEverything = () ->
        $scope.upgradeAllPlugins().then () ->
            if $scope.coreUpgradeAvailable
                $scope.upgradeCore()
            else
                notify.success 'All plugins updated'
                messagebox.show(title: 'Done', text: 'Installed. A panel restart is required.', positive: 'Restart now', negative: 'Later').then () ->
                    core.forceRestart()
        .catch () ->
            notify.error 'Some plugins failed to update'

    $scope.upgradeAllPlugins = () ->
        q = $q.defer()

        rqQs = []
        upgradeQs = []
        for plugin in $scope.installedPlugins
            upgrade = $scope.getUpgrade(plugin)
            if upgrade
                p = tasks.start('aj.plugins.plugins.tasks.InstallPlugin', [], name: upgrade.name, version: upgrade.version)
                rqQs.push p
                p.then (data) ->
                    upgradeQs.push data.promise

        if rqQs.length == 0
            q = $q.defer()
            q.resolve()
            return q.promise

        msg = messagebox.show progress: true, title: 'Updating plugins'

        $q.all(rqQs).then () ->
            $q.all(upgradeQs).then () ->
                q.resolve()
            .catch () ->
                q.reject()
            .finally () ->
                msg.close()

        return q.promise


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
        tasks.start('aj.plugins.plugins.tasks.InstallPlugin', [], name: plugin.name, version: plugin.version).then (data) ->
            data.promise.then () ->
                $scope.refresh()
                messagebox.show(title: 'Done', text: 'Installed. A panel restart is required.', positive: 'Restart now', negative: 'Later').then () ->
                    core.forceRestart()
                return null
            .catch (e) ->
                notify.error 'Install failed', e.error
            .finally () ->
                msg.close()

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
