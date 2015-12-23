angular.module('ajenti.filesystem').controller 'DiskWidgetController', ($scope) ->
    $scope.$on 'widget-update', ($event, id, data) ->
        if id != $scope.widget.id
            return
        $scope.service = data


angular.module('ajenti.filesystem').controller 'DiskWidgetConfigController', ($scope, filesystem) ->
    $scope.services = []

    filesystem.mountpoints().then (data) ->
        $scope.mountpoints = data
