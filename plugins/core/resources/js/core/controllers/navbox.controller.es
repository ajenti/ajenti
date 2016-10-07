angular.module('core').controller('CoreNavboxController', function($scope, $http, $location, hotkeys) {
    $scope.results = null;

    hotkeys.on($scope, (key, event) => {
        if (key === 'P' && event.ctrlKey) {
            $scope.visible = true;
            return true;
        }
        return false;
    }, 'keydown');

    $scope.cancel = () => {
        $scope.visible = false;
        $scope.query = null;
    };

    $scope.onSearchboxKeyDown = ($event) => {
        if ($scope.results) {
            if ($event.keyCode === hotkeys.ENTER) {
                $scope.open($scope.results[0]);
            }

            let result = [];

            let len = Math.min($scope.results.length, 10);
            for (let i = 0; j < len; i++) {
                if ($event.keyCode === i.toString().charCodeAt(0) && $event.shiftKey) {
                    $scope.open($scope.results[i]);
                    $event.preventDefault();
                }
            }
        }
    };

    $scope.onSearchboxKeyUp = ($event) => {
        if ($event.keyCode === hotkeys.ESC) {
            $scope.cancel();
        }
    };

    $scope.$watch('query', () => {
        if (!$scope.query) {
            return;
        }
        $http.get(`/api/core/navbox/${$scope.query}`).then(response => $scope.results = response.data);
    });

    $scope.open = (result) => {
        $location.path(result.url);
        $scope.cancel();
    };
});
