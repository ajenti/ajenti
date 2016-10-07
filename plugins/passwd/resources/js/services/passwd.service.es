angular.module('ajenti.passwd').service('passwd', function($http, $q) {
    this.list = () => {
        return $http.get("/api/passwd/list").then(response => response.data)
    };

    this.set = (user, password) => {
        return $http.post("/api/passwd/set", {user, password}).then(response => response.data)
    };

    return this;
});
