angular.module('ajenti.datetime').service('datetime', function($http, $q, tasks) {
    this.listTimezones = function() {
        return $http.get("/api/datetime/timezones").then(response => response.data)
    };

    this.getTimezone = function() {
        return $http.get("/api/datetime/timezone").then(response => response.data)
    };

    this.setTimezone = function(tz) {
        return $http.post(`/api/datetime/timezone/${tz}`).then(response => response.data)
    };

    this.getTime = function() {
        return $http.get(`/api/datetime/time`).then(response => response.data)
    };

    this.setTime = function(time) {
        return $http.post(`/api/datetime/time/${time}`).then(response => response.data)
    };

    this.syncTime = function() {
        return $http.post(`/api/datetime/time/sync`).then(response => response.data)
    };

    return this;
});
