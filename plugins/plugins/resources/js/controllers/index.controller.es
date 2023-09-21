angular.module('core').config($routeProvider => {
    $routeProvider.when('/view/plugins', {
        templateUrl: '/plugins:resources/partial/index.html',
        controller: 'PluginsIndexController'
    })
});

angular.module('ajenti.plugins').controller('PluginsIndexController', function($scope, $q, $http, $rootScope, notify, identity, pageTitle, messagebox, tasks, core, gettext) {
    pageTitle.set('Plugins');

    $scope.selectedInstalledPlugin = null;
    $scope.selectedRepoPlugin = null;
    $scope.coreUpgradeAvailable = null;

    $scope.selectRepoPlugin = plugin => $scope.selectedRepoPlugin = plugin;

    $scope.needUpgrade = (local_version,repo_version) => {
        if (repo_version === null) {
            notify.error(gettext('Could not load repository version for ajenti-panel.'));
            return false;
        }
        if (local_version === repo_version) {
            return false;
        }
        details_local = local_version.split('.');
        details_repo = repo_version.split('.');
        min_array_len = Math.min(details_local.length, details_repo.length);
        for (let i=0; i<=min_array_len; i++) {
            if (parseInt(details_local[i]) < parseInt(details_repo[i])) {
                return true;
            }
            // For special developer case ...
            if (parseInt(details_local[i]) > parseInt(details_repo[i])) {
                return false;
            }
        }
        // At this point, all minimal details values are equals, like e.g. 1.32 and 1.32.4
        if (details_local.length < details_repo.length) {
            return true;
        }
        return false;
    }

    $scope.refresh = () => {
        $http.get('/api/plugins/installed').then((resp) => {
            $scope.installedPlugins = resp.data;
            $scope.repoList = null;
            $scope.repoListOfficial = null;
            $scope.repoListCommunity = null;
            $http.get('/api/plugins/pypi/ajenti-plugins').then((rsp) => {
                $scope.repoList = rsp.data;
                $scope.notInstalledRepoList = $scope.repoList.filter((x) => !$scope.isInstalled(x)).map((x) => x);
                $scope.repoListOfficial = $scope.repoList.filter((x) => x.type === "official").map((x) => x);
                $scope.repoListCommunity = $scope.repoList.filter((x) => x.type !== "official").map((x) => x);
            }, (err) => {
                notify.error(gettext('Could not load plugin repository'), err.message)
            });
        }, (err) => {
            notify.error(gettext('Could not load the installed plugin list'), err.message)
        });

        $http.post('/api/plugins/core/check-upgrade').then((resp) => $scope.coreUpgradeAvailable = $scope.needUpgrade($rootScope.ajentiVersion, resp.data));

        $scope.pypiList = null;
        $http.get('/api/plugins/pypi/installed').then((resp) => $scope.pypiList = resp.data);
    };

    identity.init();
    identity.promise.then(() => {
        if (identity.isSuperuser) {
            $scope.refresh();
        }
    });

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
            if (p.name === plugin.name && $scope.needUpgrade(plugin.version,p.version)) {
                return p;
            }
        }
        return null;
    };

    $scope.installPlugin = (plugin) => {
        $scope.selectedRepoPlugin = null;
        $scope.selectedInstalledPlugin = null;
        let msg = messagebox.show({progress: true, title: 'Installing'});
        upgradeInfo = $scope.getUpgrade(plugin);
        if (upgradeInfo !== null) {
            if (upgradeInfo.version != plugin.version)
                version = upgradeInfo.version;
        }
        else
            version = plugin.version;
        return tasks.start(
            'aj.plugins.plugins.tasks.InstallPlugin',
            [],
            {name: plugin.name, version: version}
        ).then((data) => {
            data.promise.then(() => {
                $scope.refresh();
                messagebox.show({
                    title: gettext('Done'),
                    text: gettext('Installed. A panel restart is required.'),
                    positive: gettext('Restart now'),
                    negative: gettext('Later')}).then(() => core.forceRestart());
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
            return tasks.start(
                'aj.plugins.plugins.tasks.UnInstallPlugin',
                [],
                {name: plugin.name}
            ).then((data) => {
                data.promise.then(() => {
                    $scope.refresh();
                    messagebox.show({
                        title: gettext('Done'),
                        text: gettext('Uninstalled. A panel restart is required.'),
                        positive: gettext('Restart now'),
                        negative: gettext('Later')}).then(() => core.forceRestart());
                    return null;
                }, e => {
                    notify.error(gettext('Uninstall failed'), e.error)
                }).finally(() => msg.close())
            });
        });
    };

    $scope.restart = () => core.restart();
});
