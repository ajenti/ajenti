angular.module('core').controller('CoreLoginController', function($scope, $log, $rootScope, $routeParams, identity, notify, gettext) {
    $rootScope.disableExpiredSessionInterceptor = true;
    $scope.working = false;
    $scope.success = false;

    if ($routeParams.mode.indexOf('sudo:') === 0) {
        $scope.mode = 'sudo';
        $scope.username = $routeParams.mode.split(':')[1];
    } else {
        $scope.mode = $routeParams.mode;
    }

    $scope.login = () => {
        if (!$scope.username || !$scope.password) {
            return;
        }
        $scope.working = true;
        identity.auth($scope.username, $scope.password, $scope.mode).then(username => {
            $scope.success = true;
            location.href = $routeParams.nextPage || '/';
        }, error => {
            $scope.working = false;
            $log.log('Authentication failed', error);
            notify.error(gettext('Authentication failed'), error);
        });
    };
});
