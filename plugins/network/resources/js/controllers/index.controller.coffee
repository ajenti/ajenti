angular.module('ajenti.network').controller 'NetworkIndexController', ($scope, $routeParams, $timeout, messagebox, notify, pageTitle, urlPrefix, network) ->
    pageTitle.set('Network')

    $scope.knownFamilies = {
        inet: ['static', 'dhcp', 'manual', 'loopback']
        inet6: ['static', 'dhcp', 'manual', 'loopback', 'auto']
    }

    $scope.knownAddressingNames = {
        static: 'Static'
        auto: 'Auto'
        dhcp: 'DHCP'
        manual: 'Manual'
        loopback: 'Loopback'
    }

    $scope.reloadState = () ->
        $scope.state = {}
        for iface in $scope.config
            do (iface) ->
                network.getState(iface.name).then (state) ->
                    $scope.state[iface.name] = state

    $scope.reload = () ->
        $scope.config = null
        network.getConfig().then (data) ->
            $scope.config = data
            $scope.reloadState()
        network.getHostname().then (hostname) ->
            $scope.hostname = hostname

    $scope.save = () ->
        network.setConfig($scope.config).then () ->
            $scope.reload()

    $scope.reload()

    $scope.upInterface = (iface) ->
        network.up(iface.name).then () ->
            notify.success 'Interface activated'
            $scope.reloadState()

    $scope.downInterface = (iface) ->
        messagebox.show(
            title: 'Warning'
            text: 'Deactivating a network interface can lock you out of the remote session'
            positive: 'Deactivate'
            negative: 'Cancel'
        ).then () ->
            network.down(iface.name).then () ->
                notify.success 'Interface deactivated'
                $scope.reloadState()

    $scope.restartInterface = (iface) ->
        messagebox.show(
            title: 'Warning'
            text: 'Restarting a network interface can lock you out of the remote session'
            positive: 'Restart'
            negative: 'Cancel'
        ).then () ->
            network.downup(iface.name).then () ->
                $timeout () ->
                    notify.success 'Interface reactivated'
                    $scope.reloadState()
                , 2000

    $scope.setHostname = (hostname) ->
        network.setHostname(hostname).then () ->
            notify.success 'Hostname changed'
        .catch (e) ->
            notify.error 'Failed', e.message
