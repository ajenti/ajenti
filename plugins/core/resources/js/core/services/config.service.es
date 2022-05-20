angular.module('core').service('config', function($http, $q, initialConfigContent) {
    this.load = () => $http.get("/api/core/config").then(response => this.data = response.data);

    this.save = () =>
        $http.post("/api/core/config", this.data)

    this.getUserConfig = () =>
        $http.get("/api/core/user-config").then(response => response.data);

    this.setUserConfig = (config) =>
        $http.post("/api/core/user-config", config).then(response => response.data);

    this.getSmtpConfig = () =>
        $http.get("/api/core/smtp-config").then(response => response.data);

    this.setSmtpConfig = (config) =>
        $http.post("/api/core/smtp-config", config).then(response => response.data);

    this.getAuthenticationProviders = (config) =>
        $http.get("/api/core/authentication-providers").then(response => response.data);

    this.getPermissions = (config) =>
        $http.get("/api/core/permissions").then(response => response.data);

    this.data = initialConfigContent;

    // For compatibility
    this.promise = $q.resolve(this.data);

    return this;
});
