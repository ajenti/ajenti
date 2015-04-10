angular.module('ajenti.network').service 'network', ($http, $q, tasks) ->
    @getConfig = () ->
        q = $q.defer()
        $http.get("/api/network/config/get").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @setConfig = (config) ->
        q = $q.defer()
        $http.post("/api/network/config/set", config).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @getState = (iface) ->
        q = $q.defer()
        $http.get("/api/network/state/#{iface}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @up = (iface) ->
        q = $q.defer()
        $http.get("/api/network/up/#{iface}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @down = (iface) ->
        q = $q.defer()
        $http.get("/api/network/down/#{iface}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    return this
