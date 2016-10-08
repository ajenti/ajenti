angular.module('ajenti.packages').service('packages', function($http, $q, tasks) {
    this.getManagers = function() {
        return $http.get("/api/packages/managers").then(response => response.data)
    };

    this.list = function(managerId, query) {
        return $http.get(`/api/packages/list/${managerId}?query=${query}`).then(response => response.data)
    };

    this.get = function(managerId, packageId) {
        return $http.get(`/api/packages/get/${managerId}/${packageId}`).then(response => response.data)
        .error(err => q.reject(err));
    };

    this.updateLists = function(managerId) {
        return tasks.start('aj.plugins.packages.tasks.UpdateLists', [], {manager_id: managerId})
    };

    this.applySelection = function(managerId, selection) {
        return $http.post(`/api/packages/apply/${managerId}`, selection).then(response => response.data)
    };

    return this;
});
