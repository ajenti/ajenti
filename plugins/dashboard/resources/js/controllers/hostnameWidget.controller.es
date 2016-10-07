angular.module('ajenti.dashboard').controller('HostnameWidgetController', $scope => {
    $scope.$on('widget-update', ($event, id, data) => {
        if (id !== $scope.widget.id) {
            return;
        }
        $scope.hostname = data;
    })
});
