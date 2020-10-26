angular.module('ajenti.softraid').controller('SoftraidIndexController', function($scope, $http, $interval, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Softraid'));

    $scope.getResources = () => {
        $http.get('/api/softraid').then((resp) => {
            $scope.raid = resp.data;
            $scope.start_refresh();
        });
    }

    $scope.start_refresh = () => {
        if ($scope.refresh === undefined)
            $scope.refresh = $interval($scope.getResources, 30000, 0);
    }

    $scope.getResources();

    $scope.$on('$destroy', () => $interval.cancel($scope.refresh));
});

