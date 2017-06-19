angular.module('ajenti.power').service('power', function($http) {
    this.getUptime = () => $http.get("/api/power/uptime").then(response => response.data)

    this.getBatteries = () => $http.get("/api/power/batteries").then(response => response.data)

    this.getAdapters = () => $http.get("/api/power/adapters").then(response => response.data)

    this.poweroff = () => $http.get("/api/power/poweroff").then(response => response.data)

    this.reboot = () => $http.get("/api/power/reboot").then(response => response.data)

    this.suspend = () => $http.get("/api/power/suspend").then(response => response.data)

    this.hibernate = () => $http.get("/api/power/hibernate").then(response => response.data)

    return this;
});
