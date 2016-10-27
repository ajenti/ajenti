angular.module('ajenti.services').service('services', function($http) {
    this.getManagers = () => {
        return $http.get("/api/services/managers").then(response => response.data)
    };

    this.getServices = (managerId) => {
        return $http.get(`/api/services/list/${managerId}`).then(response => response.data)
    };

    this.getService = (managerId, serviceId) => {
        return $http.get(`/api/services/get/${managerId}/${serviceId}`).then(response => response.data)
    };

    this.runOperation = (service, operation) => {
        return $http.get(`/api/services/do/${operation}/${service.managerId}/${service.id}`).then(response => response.data)
    };

    return this;
});
