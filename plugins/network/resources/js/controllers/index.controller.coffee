angular.module('ajenti.network').controller 'NetworkIndexController', ($scope, $routeParams, $location, notify, pageTitle, urlPrefix, network) ->
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
        network.down(iface.name).then () ->
            notify.success 'Interface deactivated'
            $scope.reloadState()

    $scope.setHostname = (hostname) ->
        network.setHostname(hostname).then () ->
            notify.success 'Hostname changed'
        .catch (e) ->
            notify.error 'Failed', e.message
