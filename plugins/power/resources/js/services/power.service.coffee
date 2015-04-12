angular.module('ajenti.power').service 'power', ($http, $q, tasks) ->
    @getUptime = () ->
        q = $q.defer()
        $http.get("/api/power/uptime").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @getBatteries = () ->
        q = $q.defer()
        $http.get("/api/power/batteries").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @getAdapters = () ->
        q = $q.defer()
        $http.get("/api/power/adapters").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @poweroff = () ->
        q = $q.defer()
        $http.get("/api/power/poweroff").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @reboot = () ->
        q = $q.defer()
        $http.get("/api/power/reboot").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @suspend = () ->
        q = $q.defer()
        $http.get("/api/power/suspend").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @hibernate = () ->
        q = $q.defer()
        $http.get("/api/power/hibernate").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    return this