angular.module('core').service('identity', function($http, $location, $window, $timeout, $q, urlPrefix, ajentiBootstrapColor) {
    let q = $q.defer();
    this.promise = q.promise;
    this.color = ajentiBootstrapColor;

    this.init = () =>
        $http.get('/api/core/identity').success(data => {
            this.user = data.identity.user;
            this.uid = data.identity.uid;
            this.effective = data.identity.effective;
            this.elevation_allowed = data.identity.elevation_allowed;
            this.profile = data.identity.profile;
            this.machine = data.machine;
            this.color = data.color;
            this.isSuperuser = this.effective === 0;
            q.resolve();
        })
        .error(() => q.reject());

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
        })
    };

    this.login = () => $window.location.assign(`${urlPrefix}/view/login/normal/${$location.path()}`);

    this.elevate = function() {
        $http.get('/api/core/logout');
        return $timeout(() => {
            $window.location.assign(`${urlPrefix}/view/login/sudo:${this.user}/${$location.path()}`);
        }, 1000);
    };

    this.logout = function() {
        $http.get('/api/core/logout');
        return $timeout(function() {
            $window.location.assign(`${urlPrefix}/view/login/normal/${$location.path()}`);
        }, 1000);
    };

    return this;
});
