angular.module('core').controller('CorePWResetMailController', function($scope, $log, $rootScope, $routeParams, $http, $window, identity, notify, gettext, customization) {
    $rootScope.disableExpiredSessionInterceptor = true;
    $scope.mail = '';

    $scope.send_email_reset = () => {
        notify.success(gettext("If the email exists, the user will get a reset email"));
        $http.post('/api/send_password_reset', {mail: $scope.mail});
        $window.location.assign('/');
    }
});

angular.module('core').controller('CorePWResetController', function($scope, $log, $rootScope, $routeParams, $window, $http, identity, notify, gettext, customization) {
    $rootScope.disableExpiredSessionInterceptor = true;
    $scope.password1 = '';
    $scope.password2 = '';
    $scope.ready = false;
    $scope.serial_ok = false;

    $scope.serial = '';
    $scope.serial = $routeParams.serial;
    $http.post('/api/check_pw_serial', {serial:$scope.serial}).then((resp) => {
        $scope.ready = true;
        $scope.serial_ok = true;
    }, (error) => {
        $scope.ready = true;
    });

    $scope.save_password = () => {
        $http.post('/api/update_password', {serial:$scope.serial,password:$scope.password2}).then((resp) => {
            notify.success(gettext('Password successfully changed !'));
            $window.location.assign('/');
        }, (error) => {
            notify.error(gettext('An error occured while changing the password'));
        });
    }
});

