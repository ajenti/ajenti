angular.module('ajenti.dashboard').controller('MemoryWidgetController', ($scope) => {
    $scope.$on('widget-update', ($event, id, data) => {
        if (id !== $scope.widget.id) {
            return;
        }
        $scope.used = data.used;
        $scope.total = data.total;
        $scope.usage = Math.floor((100 * $scope.used) / $scope.total);
    })
});
