angular.module('core').service('identity', function($http, $location, $window, $timeout, $q, urlPrefix, ajentiBootstrapColor) {
    let q = $q.defer();
    this.promise = q.promise;
    this.color = ajentiBootstrapColor;

    this.init = () =>
        $http.get('/api/core/identity').then((resp) => {
            identity = resp.data.identity;
            this.user = identity.user;
            this.uid = identity.uid;
            this.effective = identity.effective;
            this.elevation_allowed = identity.elevation_allowed;
            this.profile = identity.profile;
            this.machine = resp.data.machine;
            this.color = resp.data.color;
            this.isSuperuser = this.effective === 0;
            q.resolve();
        }, () => q.reject());

    this.auth = (username, password, mode) => {
        let data = {
            username,
            password,
            mode
        };

        return $http.post('/api/core/auth', data).then((response) => {
            if (!response.data.success) {
                return $q.reject(response.data.error);
            }
            return $q.resolve(response);
        })
    };

    this.login = () => $window.location.assign(`${urlPrefix}/view/login/normal/${$location.path()}`);

    this.manage_totp = () => $window.location.assign(`${urlPrefix}/view/totp`);

    this.elevate = function() {
        return $timeout(() => {
            $window.location.assign(`${urlPrefix}/view/login/sudo:${this.user}/${$location.path()}`);
        }, 1000);
    };

    this.logout = function() {
        $http.post('/api/core/logout');
        return $timeout(function() {
            $window.location.assign(`${urlPrefix}/view/login/normal/${$location.path()}`);
        }, 1000);
    };

    return this;
});
