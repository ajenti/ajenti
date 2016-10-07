angular.module('core').service('config', function($http, $q, initialConfigContent) {
    this.load = () => $http.get("/api/core/config").then(response => this.data = response.data);

    this.save = () =>
        $http.post("/api/core/config", this.data)

    this.getUserConfig = () =>
        $http.get("/api/core/user-config").then(response => response.data);

    this.setUserConfig = (config) =>
        $http.post("/api/core/user-config", config).then(response => response.data);

    this.getAuthenticationProviders = (config) =>
        $http.post("/api/core/authentication-providers", config).then(response => response.data);

    this.getPermissions = (config) =>
        $http.post("/api/core/permissions", config).then(response => response.data);

    this.data = initialConfigContent;

    // For compatibility
    this.promise = $q.resolve(this.data);

    return this;
});
