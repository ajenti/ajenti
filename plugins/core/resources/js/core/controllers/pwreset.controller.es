angular.module('core').controller('CorePWResetMailController', function($scope, $log, $rootScope, $routeParams, $http, identity, notify, gettext, customization) {
    $rootScope.disableExpiredSessionInterceptor = true;
    $scope.mail = '';

    $scope.send_email_reset = () => {
        $http.post('/api/send_password_reset', {mail: $scope.mail});
        notify.success(gettext("If the email exists, the user will get a reset email"));
    }
});

angular.module('core').controller('CorePWResetController', function($scope, $log, $rootScope, $routeParams, $http, identity, notify, gettext, customization) {
    $rootScope.disableExpiredSessionInterceptor = true;

    $scope.serial = '';
    $scope.serial = $routeParams.serial;
    $http.post('/api/check_pw_serial', {serial:$scope.serial}).then((resp) => {
        console.log(resp.data);
        notify.success(gettext("Password successfully changed!"));
    }, (error) => {
        notify.error(gettext("Error"));
    });
});

