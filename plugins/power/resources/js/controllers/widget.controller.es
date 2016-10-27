angular.module('ajenti.power').controller('PowerWidgetController', ($scope, services) => {
    $scope.$on('widget-update', ($event, id, data) => {
        if (id !== $scope.widget.id) {
            return;
        }
        $scope.batteries = data.batteries;
        $scope.adapters = data.adapters;
    })
});
