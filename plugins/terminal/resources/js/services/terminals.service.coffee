angular.module('ajenti.terminal').service 'terminals', ($http, $q) ->
    @script = (options) ->
        q = $q.defer()
        $http.post('/api/terminal/script', options).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @list = () ->
        q = $q.defer()
        $http.get("/api/terminal/list").success (data) ->
            for t in data
                cmd = t.command.split(' ')[0]
                tokens = cmd.split('/')
                t.title = tokens[tokens.length - 1]
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @kill = (id) ->
        q = $q.defer()
        $http.get("/api/terminal/kill/#{id}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @create = (options) ->
        options ?= {}
        q = $q.defer()
        $http.post("/api/terminal/create", options).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @full = (id) ->
        q = $q.defer()
        $http.get("/api/terminal/full/#{id}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    return this
