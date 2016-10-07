angular.module('ajenti.dashboard').service('dashboard', function($http, $q) {
    this.getAvailableWidgets = () => {
        return $http.get("/api/dashboard/widgets").then(response => response.data)
    };

    this.getValues = function(data) {
        return $http.post("/api/dashboard/get-values", data, {ignoreLoadingBar: true}).then(response => response.data)
    };

    return this;
});
