angular.module('ajenti.traffic').controller('TrafficWidgetController', ($scope, notify) => {
    $scope.oldData = {};
    $scope.oldTimestamp = null;

    $scope.$on('widget-update', ($event, id, data) => {
        if (id !== $scope.widget.id || !data) {
            return;
        }
        $scope.txTotal = data.tx;
        $scope.rxTotal = data.rx;

        if ($scope.oldTimestamp) {
            let dt = (new Date().getTime() - $scope.oldTimestamp) / 1000.0;
            $scope.txSpeed = (data.tx - $scope.oldData.tx) / dt;
            $scope.rxSpeed = (data.rx - $scope.oldData.rx) / dt;
        }

        $scope.oldTimestamp = new Date().getTime();
        $scope.oldData = data;
    });
});


angular.module('ajenti.traffic').controller('TrafficWidgetConfigController', ($scope, $http) => {
    $scope.traffic = [];
    $http.get('/api/traffic/interfaces').success(interfaces => $scope.interfaces = interfaces);
});
