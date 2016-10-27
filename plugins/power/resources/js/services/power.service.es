angular.module('ajenti.power').service('power', function($http) {
    this.getUptime = () => $http.get("/api/power/uptime").success(response => response.data)

    this.getBatteries = () => $http.get("/api/power/batteries").success(response => response.data)

    this.getAdapters = () => $http.get("/api/power/adapters").success(response => response.data)

    this.poweroff = () => $http.get("/api/power/poweroff").success(response => response.data)

    this.reboot = () => $http.get("/api/power/reboot").success(response => response.data)

    this.suspend = () => $http.get("/api/power/suspend").success(response => response.data)

    this.hibernate = () => $http.get("/api/power/hibernate").success(response => response.data)

    return this;
});
