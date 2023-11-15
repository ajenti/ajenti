angular.module('ajenti.power').service('power', function($http) {
    this.getUptime = () => $http.get("/api/power/uptime").then(response => response.data)

    this.getBatteries = () => $http.get("/api/power/batteries").then(response => response.data)

    this.getAdapters = () => $http.get("/api/power/adapters").then(response => response.data)

    this.poweroff = () => $http.post("/api/power/command_power", {'command': 'poweroff'}).then(response => response.data)

    this.reboot = () => $http.post("/api/power/command_power", {'command': 'reboot'}).then(response => response.data)

    this.suspend = () => $http.post("/api/power/command_power", {'command': 'suspend'}).then(response => response.data)

    this.hibernate = () => $http.post("/api/power/command_power", {'command': 'hibernate'}).then(response => response.data)

    return this;
});
