angular.module('ajenti.augeas').service('augeas', function($http, $q, AugeasConfig) {
    this.get = (endpoint) => {
        return $http.get(`/api/augeas/endpoint/get/${endpoint}`).then(response => AugeasConfig.get(response.data))
    };

    this.set = (endpoint, config) => {
        return $http.post(`/api/augeas/endpoint/set/${endpoint}`, config.serialize()).then(response => response.data)
    };

    return this;
});
