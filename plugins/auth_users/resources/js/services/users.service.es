angular.module('ajenti.auth.users').service('users', function($http, $q) {
    this.load = () => $http.get("/api/auth-users/config").then(response => this.data = response.data);

    this.save = () =>
        $http.post("/api/auth-users/config", this.data)

    this.getPermissions = (config) =>
        $http.post("/api/auth-users/permissions", config).then(response => response.data);

    this.data = {};

    return this;
});
