angular.module('core').controller('CoreTotpController', function($scope, $log, $rootScope, $routeParams, $http, $window, identity, notify, gettext, customization) {
    $scope.add_new = false;
    identity.promise.then(() => $scope.user = identity.user);

    //$http.get('/api/core/user-config').then((resp) => $scope.totp = resp.data.totp || '');
    $http.get('/api/core/totps').then((resp) => {
        $scope.totp = resp.data || '';
        console.log(resp.data);
    });

    $scope.random_secret = () => {
        // Generate a random 16-strings in base32
        secret = '';
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
        for ( var i = 0; i < 16; i++ ) {
            secret += chars.charAt(Math.floor(Math.random() * 32));
        }
        $scope.tmp_totp.secret = secret;
        $scope.tmp_qr = $scope.update_tmp_qr();
    };

    $scope.add = () => {
        $scope.add_new = true;
        $scope.tmp_totp = {
            'user': $scope.user,
            'description': '',
            'secret': '',
        };
        $scope.random_secret();
        $scope.verified = false;
    }

    $scope.closeDialog = () => $scope.add_new = false;

    $scope.update_tmp_qr = () => {
        $http.post('/api/core/totps/qr', {'user': $scope.tmp_totp.user, 'secret': $scope.tmp_totp.secret}).then((resp) => $scope.tmp_qr = resp.data);
    }

    $scope.verify = ($event) => {
        code = $event.verif_code;
        if (code.toString().length == 6) {
            $http.post('/api/core/totps/verify', {
                'user': $scope.tmp_totp.user,
                'secret': $scope.tmp_totp.secret,
                'code': code}).then((resp) => $scope.verified = resp.data)
        }
    }

    $scope.delete = (timestamp) => {
        $http.delete(`/api/core/totps/${timestamp}`).then((resp) => notify.success('Done'));
    }

    $scope.save = () => {
        console.warn("saved");
        $scope.closeDialog();
    }
});

