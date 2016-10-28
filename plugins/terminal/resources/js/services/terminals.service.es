angular.module('ajenti.terminal').service('terminals', function($http, $q, $location) {
    this.script = function(options) {
        return $http.post('/api/terminal/script', options).then(response => response.data)
    };

    this.list = function() {
        return $http.get("/api/terminal/list").then((response) => {
            for (let terminal of response.data) {
                let cmd = terminal.command.split(' ')[0];
                let tokens = cmd.split('/');
                terminal.title = tokens[tokens.length - 1];
            }
            return response.data;
        })
    };

    this.kill = function(id) {
        return $http.get(`/api/terminal/kill/${id}`).then(response => response.data)
    };

    this.create = function(options) {
        if (typeof options === 'undefined' || options === null) { options = {}; }
        return $http.post("/api/terminal/create", options).then(response => response.data)
    };

    this.full = function(id) {
        return $http.get(`/api/terminal/full/${id}`).then(response => response.data)
    };

    this.navigate = id => $location.path(`/view/terminal/${id}`);

    return this;
});
