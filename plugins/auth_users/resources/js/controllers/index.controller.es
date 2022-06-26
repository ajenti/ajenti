angular.module('ajenti.auth.users').controller('AuthUsersIndexController', function($scope, $http, notify, pageTitle, config, users, passwd, customization, gettext) {
    pageTitle.set('Users');

    $scope.defaultRootPassword = '73637279707400100000000800000001f77e545afaeced51bdc33d16311ae24d900fbd462f444bce13d3c2aec489f90996523b8f779955a0f67708e0164de989c91a9a8093cd422fd5f5727018bb790f8aa36363273f5415660e7ff5c9fb9432e1f8ef5a3e35604ab9f2549aa85dbf2ca842573d25c02753bee5f0dd9c542b5ec51d58b443ad9f5e2b8dd9de8bd63a70908a1283c290bc7ccab30a3a88553ef23f5a6c25ccbe82e9f2b9ea656a6e373c33897e7b6376992de5cd00e78ed940486cd7bf0634ab1a1be2cf2f14ba2beabd55f82f5f3859ee9eea350c0a9fa9495749f0d0d6db21c5c17c742263e0e5bfb5c1c964edec1579c92ea538566151581bd06756564c21796eb61a0dd6d42b95ea5b1cdf667e0b06450622882fbf0bc7c9274903fd920368742769ee70e24a6d917afe6ba28faca235bcb83a1e22f37ee867d843b023424885623470940dd17c244a8f0ef998f29e5b680721d656c2a610609534e47ece10ea164b884d11ce983148aacf84044c5336bbc167fd28f45438'; // 'admin'

    users.load().then(() => {
        $scope.users = users;
        if (users.data.users == null || Object.keys(users.data.users).length == 0) {
            users.data.users = {
                root: {
                    password: $scope.defaultRootPassword,
                    uid: 0
                }
            };
            notify.warning(gettext('No user actually saved. You should save this configuration to permit at least root login.'));
        }

        $scope.isDangerousSetup = () => {
            if (!users.data) {
                return false;
            }
            let safe = false;
            for (let username in users.data.users) {
                if (users.data.users[username].uid === 0) {
                    safe = true;
                }
            }
            return !safe;
        };

        config.getAuthenticationProviders(config).then((data) => {
            for (let auth_provider of data) {
                if (auth_provider.id == 'users') {
                    $scope.otherAuthProv = !auth_provider.used;
                }
            }
        });

        config.getPermissions(config).then((data) => {
            $scope.permissions = data;
            let result = [];
            for (let username in users.data.users) {
                $scope.resetPermissions(username);
                result.push(angular.extend($scope.userPermissions[username], users.data.users[username].permissions || {}));
            }
            return result;
        });
    }).catch(() => notify.error('Could not load config'));

    $scope.userPermissions = {};
    $scope.resetPermissions = (username) => {
        $scope.userPermissions[username] = {};
        $scope.permissions.forEach(permission => {
            $scope.userPermissions[username][permission.id] = permission.default;
        });
    };

    $scope.removeUser = username => delete users.data.users[username];

    passwd.list().then(l => {
        $scope.systemUsers = l;

        $scope.getSystemUser = (uid) => {
            for (let u of $scope.systemUsers) {
                if (u.uid === uid) {
                    return u;
                }
            }
        };
    });

    $scope.save = function() {
        for (let username in $scope.userPermissions) {
            if (!users.data.users[username]) {
                continue;
            }
            users.data.users[username].permissions = {};
            for (let permission of $scope.permissions) {
                let v = $scope.userPermissions[username][permission.id];
                if (v !== permission.default) {
                    users.data.users[username].permissions[permission.id] = v;
                }
            }
        }

        users.save().then(() => notify.success('Saved'));
    };

    $scope.setPassword = (username, password) => {
        users.save().then(() =>
            $http.post(`/api/auth-users/password/${username}`, password).then(function() {
                notify.success(gettext('Password updated'));
                users.load();
            })
        )
    };

    $scope.addUser = (username) => {
        if (Object.keys(users.data.users).indexOf(username) > -1) {
            notify.error(gettext('This username is already taken'));
            return;
        }
        users.data.users[username] = {uid: customization.plugins.auth_users.forceUID || 0};
        $scope.resetPermissions(username);
        $scope.configuringUsername = username;
        $scope.newUsername = '';
    };

});
