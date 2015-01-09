angular.module('util.filesystem').service 'filesystem', ($http, $q) ->
    @read = (path) ->
        q = $q.defer()
        $http.get("/api/filesystem/read/#{path}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @write = (path, content) ->
        q = $q.defer()
        $http.post("/api/filesystem/write/#{path}", content).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @list = (path) ->
        q = $q.defer()
        $http.get("/api/filesystem/list/#{path}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise
        
    return this
