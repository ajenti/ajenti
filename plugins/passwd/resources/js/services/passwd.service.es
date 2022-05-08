angular.module('ajenti.passwd').service('passwd', function($http, $q) {
    this.list = () => {
        return $http.get("/api/passwds").then(response => response.data)
    };

    this.set = (user, password) => {
        return $http.post("/api/passwd", {user, password}).then(response => response.data)
    };

    return this;
});
