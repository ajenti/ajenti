angular.module('ajenti.settings').service 'settings', ($http, $q) ->
    @getConfig = () ->
        q = $q.defer()
        $http.get("/api/settings/config").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @setConfig = (config) ->
        q = $q.defer()
        $http.post("/api/settings/config", config).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @getUserConfig = () ->
        q = $q.defer()
        $http.get("/api/settings/user-config").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @setUserConfig = (config) ->
        q = $q.defer()
        $http.post("/api/settings/user-config", config).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    return this
