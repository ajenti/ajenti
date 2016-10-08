angular.module('ajenti.network').controller('NetworkIndexController', function($scope, $routeParams, $timeout, messagebox, notify, pageTitle, network, gettext) {
    pageTitle.set(gettext('Network'));

    $scope.knownFamilies = {
        inet: ['static', 'dhcp', 'manual', 'loopback'],
        inet6: ['static', 'dhcp', 'manual', 'loopback', 'auto']
    };

    $scope.knownAddressingNames = {
        static: gettext('Static'),
        auto: gettext('Auto'),
        dhcp: 'DHCP',
        manual: gettext('Manual'),
        loopback: gettext('Loopback')
    };

    $scope.reloadState = () => {
        $scope.state = {};
        $scope.config.forEach((iface) =>
            (iface =>
                network.getState(iface.name).then(state => $scope.state[iface.name] = state)
            )(iface));
    };

    $scope.reload = () => {
        $scope.config = null;
        network.getConfig().then((data) => {
            $scope.config = data;
            $scope.reloadState();
        });
        network.getHostname().then(hostname => $scope.hostname = hostname);
    };

    $scope.save = () =>
        network.setConfig($scope.config).then(() => $scope.reload());

    $scope.reload();

    $scope.upInterface = (iface) =>
        network.up(iface.name).then(() => {
            notify.success(gettext('Interface activated'));
            $scope.reloadState();
        });

    $scope.downInterface = (iface) =>
        messagebox.show({
            title: gettext('Warning'),
            text: gettext('Deactivating a network interface can lock you out of the remote session'),
            positive: gettext('Deactivate'),
            negative: gettext('Cancel')
        }).then(() =>
            network.down(iface.name).then(() => {
                notify.success(gettext('Interface deactivated'));
                $scope.reloadState();
            })
        );

    $scope.restartInterface = (iface) =>
        messagebox.show({
            title: gettext('Warning'),
            text: gettext('Restarting a network interface can lock you out of the remote session'),
            positive: gettext('Restart'),
            negative: gettext('Cancel')
        }).then(() =>
            network.downup(iface.name).then(() =>
                $timeout(() => {
                    notify.success(gettext('Interface reactivated'));
                    return $scope.reloadState();
                }, 2000)
            )
        );

    $scope.setHostname = (hostname) =>
        network.setHostname(hostname).then(() => {
            notify.success(gettext('Hostname changed'))
        }, e => {
            notify.error(gettext('Failed'), e.message)
        });
});
