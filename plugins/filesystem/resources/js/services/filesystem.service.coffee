angular.module('ajenti.filesystem').service 'filesystem', ($http, $q) ->
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

    @stat = (path) ->
        q = $q.defer()
        $http.get("/api/filesystem/stat/#{path}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @chmod = (path, mode) ->
        q = $q.defer()
        $http.post("/api/filesystem/chmod/#{path}", mode: mode).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @createFile = (path, mode) ->
        q = $q.defer()
        $http.post("/api/filesystem/create-file/#{path}", mode: mode).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @createDirectory = (path, mode) ->
        q = $q.defer()
        $http.post("/api/filesystem/create-directory/#{path}", mode: mode).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    return this
