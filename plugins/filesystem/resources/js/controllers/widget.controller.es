angular.module('ajenti.filesystem').controller('DiskWidgetController', $scope =>
    $scope.$on('widget-update', function($event, id, data) {
        if (id !== $scope.widget.id) {
            return;
        }
        return $scope.service = data;
    }
    )

);


angular.module('ajenti.filesystem').controller('DiskWidgetConfigController', function($scope, filesystem) {
    $scope.services = [];

    return filesystem.mountpoints().then(data => $scope.mountpoints = data);
}
);
