angular.module('core').config($routeProvider => {
    $routeProvider.when('/view/plugins', {
        templateUrl: '/plugins:resources/partial/index.html',
        controller: 'PluginsIndexController'
    })
});

angular.module('ajenti.plugins').controller('PluginsIndexController', function($scope, $q, $http, notify, pageTitle, messagebox, tasks, core, gettext) {
    pageTitle.set('Plugins');

    $scope.officialKeyFingerprint = '425E 018E 2394 4B4B 4281  4EE0 BDC3 FBAA 5302 9759';
    $scope.selectedInstalledPlugin = null;
    $scope.selectedRepoPlugin = null;
    $scope.coreUpgradeAvailable = null;

    $scope.selectRepoPlugin = plugin => $scope.selectedRepoPlugin = plugin;

    $scope.refresh = () => {
        $http.get('/api/plugins/list/installed').success((data) => {
            $scope.installedPlugins = data;
            $scope.repoList = null;
            $scope.repoListOfficial = null;
            $scope.repoListCommunity = null;
            $http.get('/api/plugins/repo/list').success((data) => {
                $scope.repoList = data;
                $scope.notInstalledRepoList = $scope.repoList.filter((x) => !$scope.isInstalled(x)).map((x) => x);
                $scope.repoListOfficial = $scope.repoList.filter((x) => x.signature === $scope.officialKeyFingerprint).map((x) => x);
                $scope.repoListCommunity = $scope.repoList.filter((x) => x.signature !== $scope.officialKeyFingerprint).map((x) => x);
            }, err => {
                notify.error(gettext('Could not load plugin repository'), err.message)
            });
        }, (err) => {
            notify.error(gettext('Could not load the installed plugin list'), err.message)
        });

        $http.get('/api/plugins/core/check-upgrade').success(data => $scope.coreUpgradeAvailable = data);

        $scope.pypiList = null;
        $http.get('/api/plugins/pypi/list').success(data => $scope.pypiList = data);
    };

    $scope.refresh();

    $scope.isInstalled = (plugin) => {
        if (!$scope.isInstalled) {
            return false;
        }
        for (let p of $scope.installedPlugins) {
            if (p.name === plugin.name) {
                return true;
            }
        }
        return false;
    };

    $scope.isUninstallable = plugin => $scope.pypiList && $scope.pypiList[plugin.name] && plugin.name !== 'core';

    $scope.isAnythingUpgradeable = () => {
        if (!$scope.installedPlugins) {
            return false;
        }
        if ($scope.coreUpgradeAvailable) {
            return true;
        }
        for (let p of $scope.installedPlugins) {
            if ($scope.getUpgrade(p)) {
                return true;
            }
        }
        return false;
    };

    $scope.upgradeEverything = () =>
        tasks.start(
            'aj.plugins.plugins.tasks.UpgradeAll', [], {}
        )
        .then(data => data.promise)
        .then(() => {
            notify.success(gettext('All plugins updated'));
            messagebox.show({
                title: gettext('Done'),
                text: gettext('Installed. A panel restart is required.'),
                positive: gettext('Restart now'),
                negative: gettext('Later')
            }).then(() => core.forceRestart());
        })
        .catch(() => {
            notify.error(gettext('Some plugins failed to update'))
        });

    $scope.getUpgrade = (plugin) => {
        if (!$scope.repoList || !plugin) {
            return null;
        }
        for (let p of $scope.repoList) {
            if (p.name === plugin.name && p.version !== plugin.version) {
                return p;
            }
        }
        return null;
    };

    $scope.installPlugin = (plugin) => {
        $scope.selectedRepoPlugin = null;
        $scope.selectedInstalledPlugin = null;
        let msg = messagebox.show({progress: true, title: 'Installing'});
        return tasks.start(
            'aj.plugins.plugins.tasks.InstallPlugin',
            [],
            {name: plugin.name, version: plugin.version}
        ).then((data) => {
            data.promise.then(() => {
                $scope.refresh();
                messagebox.show({title: gettext('Done'), text: gettext('Installed. A panel restart is required.'), positive: gettext('Restart now'), negative: gettext('Later')}).then(() => core.forceRestart());
                return null;
            }, e => {
                notify.error(gettext('Install failed'), e.error)
            }).finally(() => msg.close())
        });
    };

    $scope.uninstallPlugin = (plugin) => {
        if (plugin.name === 'plugins') {
            return messagebox.show({
                title: gettext('Warning'),
                text: gettext('This will remove the Plugins plugin. You can reinstall it later using PIP.'),
                positive: gettext('Continue'),
                negative: gettext('Cancel')
            }).then(() => {
                return $scope.doUninstallPlugin(plugin)
            });
        } else {
            return $scope.doUninstallPlugin(plugin);
        }
    };

    $scope.doUninstallPlugin = (plugin) => {
        $scope.selectedRepoPlugin = null;
        $scope.selectedInstalledPlugin = null;
        return messagebox.show({
            title: gettext('Uninstall'),
            text: gettext(`Uninstall ${plugin.name}?`),
            positive: gettext('Uninstall'),
            negative: gettext('Cancel')
        }).then(() => {
            let msg = messagebox.show({progress: true, title: gettext('Uninstalling')});
            return $http.get(`/api/plugins/pypi/uninstall/${plugin.name}`).success(() => {
                $scope.refresh();
                return messagebox.show({
                    title: gettext('Done'),
                    text: gettext('Uninstalled. A panel restart is required.'),
                    positive: gettext('Restart now'),
                    negative: gettext('Later')
                }).then(() => {
                    core.forceRestart()
                });
            }, (err) => {
                notify.error(gettext('Uninstall failed'), err.message)
            }).finally(() => {
                msg.close()
            });
        });
    };

    $scope.restart = () => core.restart();
});
