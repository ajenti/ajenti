angular.module('core').controller('CoreLoginController', function($scope, $log, $rootScope, $routeParams, identity, notify, gettext, customization) {
    $rootScope.disableExpiredSessionInterceptor = true;
    $scope.working = false;
    $scope.success = false;
    $scope.verif_code = false;
    $scope.showPWReset = $rootScope.pwReset == 'True';
    $scope.showPassword = false;
    $scope.totp_attempts = 0;

    $scope.toggleShowPassword = () => $scope.showPassword = !$scope.showPassword;

    identity.init();

    if ($routeParams.mode.indexOf('sudo:') === 0) {
        $scope.mode = 'sudo';
        $scope.username = $routeParams.mode.split(':')[1];
    } else {
        $scope.mode = $routeParams.mode;
    }

    identity.promise.then(() => {
        // Already identified ? Then redirect to /
        if (identity.user !== null && $scope.mode != 'sudo') {
            location.href = '/';
        }
    });

    $scope.sanitizeNextPage = () => {
        // Avoid some unwanted redirections
        if ($routeParams.nextPage !== undefined) {
            if ($routeParams.nextPage.substring(0, 1) != '/') {
                return '/'
            } else {
                return $routeParams.nextPage
            }
        }
        return '/'
    }

    $scope.verify = ($event) => {
        code = $event.code;
        if (code.toString().length == 6) {
            $scope.totp_attempts++;
            identity.auth($scope.username, code, "totp").then((response) => {
                $scope.success = true;
                nextPage = $scope.sanitizeNextPage();
                location.href = customization.plugins.core.loginredir || nextPage;
            }, error => {
                $event.code = "";
                $log.log('Wrong TOTP', error);
                notify.error(gettext('Wrong TOTP'));
                if ($scope.totp_attempts == 3) {
                    $scope.closeTotpDialog();
                }
            });
        }
    }

    $scope.closeTotpDialog = () => {
        $scope.working = false;
        $scope.verif_code = false;
        $scope.totp_attempts = 0;
        $scope.username = '';
        $scope.password = '';
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
            nextPage = $scope.sanitizeNextPage();
            location.href = customization.plugins.core.loginredir || nextPage;
        }, error => {
            $scope.working = false;
            if ($scope.mode == 'sudo') {
                $log.log('Sudo authentication failed from ' + $scope.username, error);
                notify.error(gettext('Sudo authentication failed. Are you in the sudo group?'));

            } else {
                $log.log('Authentication failed from ' + $scope.username, error);
                notify.error(gettext('Authentication failed'));
            }
        });
    };
});
