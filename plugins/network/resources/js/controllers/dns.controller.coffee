angular.module('ajenti.network').controller 'NetworkDNSController', ($scope, notify, augeas) ->
    augeas.get('resolv').then (config) ->
        $scope.config = config

    $scope.addNameserver = () ->
        $scope.config.insert 'nameserver', $scope.newNameserver
        $scope.newNameserver = ''

    $scope.save = () ->
        augeas.set('resolv', $scope.config).then () ->
            notify.success 'Saved'
        .catch (e) ->
            notify.error 'Could not save', e.message
            