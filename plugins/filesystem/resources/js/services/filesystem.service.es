angular.module('ajenti.filesystem').service('filesystem', function($http, $q) {
    this.mountpoints = function() {
        let q = $q.defer();
        $http.get("/api/filesystem/mountpoints").success(data => q.resolve(data))
        .error(err => q.reject(err));
        return q.promise;
    };

    this.read = function(path, encoding) {
        let q = $q.defer();
        $http.get(`/api/filesystem/read/${path}?encoding=${encoding || 'utf-8'}`).success(data => q.resolve(data))
        .error(err => q.reject(err));
        return q.promise;
    };

    this.write = function(path, content, encoding) {
        let q = $q.defer();
        $http.post(`/api/filesystem/write/${path}?encoding=${encoding || 'utf-8'}`, content).success(data => q.resolve(data))
        .error(err => q.reject(err));
        return q.promise;
    };

    this.list = function(path) {
        let q = $q.defer();
        $http.get(`/api/filesystem/list/${path}`).success(data => q.resolve(data))
        .error(err => q.reject(err));
        return q.promise;
    };

    this.stat = function(path) {
        let q = $q.defer();
        $http.get(`/api/filesystem/stat/${path}`).success(data => q.resolve(data))
        .error(err => q.reject(err));
        return q.promise;
    };

    this.chmod = function(path, mode) {
        let q = $q.defer();
        $http.post(`/api/filesystem/chmod/${path}`, {mode}).success(data => q.resolve(data))
        .error(err => q.reject(err));
        return q.promise;
    };

    this.createFile = function(path, mode) {
        let q = $q.defer();
        $http.post(`/api/filesystem/create-file/${path}`, {mode}).success(data => q.resolve(data))
        .error(err => q.reject(err));
        return q.promise;
    };

    this.createDirectory = function(path, mode) {
        let q = $q.defer();
        $http.post(`/api/filesystem/create-directory/${path}`, {mode}).success(data => q.resolve(data))
        .error(err => q.reject(err));
        return q.promise;
    };

    this.downloadBlob = (content, mime, name) =>
        setTimeout(function() {
            let blob = new Blob([content], {type: mime});
            let elem = window.document.createElement('a');
            elem.href = URL.createObjectURL(blob);
            elem.download = name;
            document.body.appendChild(elem);
            elem.click();
            return document.body.removeChild(elem);
        })
    ;

    return this;
}
);
