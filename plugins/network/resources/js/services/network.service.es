angular.module('ajenti.network').service('network', function($http, $q, tasks) {
    this.getConfig = () => {
        return $http.get("/api/network/config").then(response => response.data)
    };

    this.setConfig = (config) => {
        return $http.post("/api/network/config", config).then(response => response.data)
    };

    this.getState = (iface) => {
        return $http.get(`/api/network/state/${iface}`).then(response => response.data)
    };

    this.up = (iface) => {
        return $http.post(`/api/network/up/${iface}`).then(response => response.data)
    };

    this.down = (iface) => {
        return $http.post(`/api/network/down/${iface}`).then(response => response.data)
    };

    this.downup = (iface) => {
        return $http.post(`/api/network/downup/${iface}`).then(response => response.data)
    };

    this.getHostname = () => {
        return $http.get("/api/network/hostname").then(response => response.data)
    };

    this.setHostname = (hostname) => {
        return $http.post("/api/network/hostname", hostname).then(response => response.data)
    };

    return this;
});
