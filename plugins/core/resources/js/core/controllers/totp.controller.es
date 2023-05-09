angular.module('core').controller('CoreTotpController', function($scope, $log, $rootScope, $routeParams, $http, $window, identity, notify, gettext, messagebox, customization) {
    $scope.add_new = false;
    identity.promise.then(() => $scope.user = identity.user);
    $scope.tmp_totp = {
        'description': '',
        'secret': ''
    };

    $http.get('/api/core/totps').then((resp) => {
        $scope.totp = resp.data || '';
    });

    $scope.random_secret = () => {
        // Generate a random 16-strings in base32
        secret = '';
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
        for ( var i = 0; i < 32; i++ ) {
            secret += chars.charAt(Math.floor(Math.random() * 32));
        }
        $scope.tmp_totp.secret = secret;
        $scope.tmp_qr = $scope.update_tmp_qr();
    };

    $scope.add = () => {
        $scope.add_new = true;
        $scope.random_secret();
        $scope.verified = false;
    }

    $scope.closeDialog = () => $scope.add_new = false;

    $scope.valid_secret = (secret) => {
        return /^[ABCDEFGHIJKLMNOPQRSTUVWXYZ234567]{32,}$/.test($scope.tmp_totp.secret);
    }

    $scope.update_tmp_qr = () => {
        $scope.tmp_totp.secret = $scope.tmp_totp.secret.toUpperCase();
        if ($scope.valid_secret($scope.tmp_totp.secret)) {
            $http.post('/api/core/totps/qr', {'secret': $scope.tmp_totp.secret}).then((resp) => $scope.tmp_qr = resp.data);
        }
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

    $scope.delete = (totp) => {
        messagebox.show({
            text: gettext('Really delete this TOTP?'),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(() => {
            $http.delete(`/api/core/totps/${totp.created}`).then((resp) => {
                notify.success(gettext('Command successfully sent'));
                position = $scope.totp.indexOf(totp);
                $scope.totp.splice(position, 1);
            });
        });
    }

    $scope.save = () => {
        $scope.tmp_totp.created = Math.floor(Date.now()/1000);
        $http.post('/api/core/totps', {'secret': $scope.tmp_totp}).then((resp) => {
            notify.success(gettext('Command successfully sent'));
            $scope.totp.push($scope.tmp_totp);
            $scope.tmp_totp = {
                'description': '',
                'secret': ''
            };
        });
        $scope.closeDialog();
    }
});

