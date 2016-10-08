angular.module('ajenti.datetime').service('datetime', function($http, $q, tasks) {
    this.listTimezones = function() {
        return $http.get("/api/datetime/tz/list").then(response => response.data)
    };

    this.getTimezone = function() {
        return $http.get("/api/datetime/tz/get").then(response => response.data)
    };

    this.setTimezone = function(tz) {
        return $http.get(`/api/datetime/tz/set/${tz}`).then(response => response.data)
    };

    this.getTime = function() {
        return $http.get(`/api/datetime/time/get`).then(response => response.data)
    };

    this.setTime = function(time) {
        return $http.get(`/api/datetime/time/set/${time}`).then(response => response.data)
    };

    this.syncTime = function() {
        return $http.get(`/api/datetime/time/sync`).then(response => response.data)
    };

    return this;
});
