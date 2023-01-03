angular.module('core').controller('CoreLoginController', function($scope, $log, $rootScope, $routeParams, identity, notify, gettext, customization) {
    $rootScope.disableExpiredSessionInterceptor = true;
    $scope.working = false;
    $scope.success = false;
    $scope.verif_code = false;
    $scope.showPWReset = $rootScope.pwReset == 'True';
    $scope.showPassword = false;

    $scope.toggleShowPassword = () => $scope.showPassword = !$scope.showPassword;

    if ($routeParams.mode.indexOf('sudo:') === 0) {
        $scope.mode = 'sudo';
        $scope.username = $routeParams.mode.split(':')[1];
    } else {
        $scope.mode = $routeParams.mode;
    }

    $scope.verify = ($event) => {
        code = $event.code;
        if (code.toString().length == 6) {
            identity.auth($scope.username, code, "totp").then((response) => {
                $scope.success = true;
                location.href = customization.plugins.core.loginredir || $routeParams.nextPage || '/';
            }, error => {
                $scope.working = false;
                $event.code = "";
                $log.log('Wrong TOTP', error);
                notify.error(gettext('Wrong TOTP'));
            });
        }
    }

    $scope.closeTotpDialog = () => {
        $scope.working = false;
        $scope.verif_code = false;
    }

    $scope.login = () => {
        if (!$scope.username || !$scope.password) {
            return;
        }
        $scope.working = true;
        $scope.username = $scope.username.toLowerCase();
        identity.auth($scope.username, $scope.password, $scope.mode).then((response) => {
            if (response.data.totp) {
               $scope.verif_code = true;
               return
            }
            $scope.success = true;
            location.href = customization.plugins.core.loginredir || $routeParams.nextPage || '/';
        }, error => {
            $scope.working = false;
            $log.log('Authentication failed', error);
            notify.error(gettext('Authentication failed'));
        });
    };
});
