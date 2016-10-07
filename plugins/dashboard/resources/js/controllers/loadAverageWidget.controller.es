angular.module('ajenti.dashboard').controller('LoadAverageWidgetController', ($scope) => {
    $scope.$on('widget-update', ($event, id, data) => {
        if (id !== $scope.widget.id) {
            return;
        }
        $scope.load = data;
    })
});
