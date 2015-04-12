angular.module('ajenti.datetime').service 'datetime', ($http, $q, tasks) ->
    @listTimezones = () ->
        q = $q.defer()
        $http.get("/api/datetime/tz/list").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @getTimezone = () ->
        q = $q.defer()
        $http.get("/api/datetime/tz/get").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @setTimezone = (tz) ->
        q = $q.defer()
        $http.get("/api/datetime/tz/set/#{tz}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @getTime = () ->
        q = $q.defer()
        $http.get("/api/datetime/time/get").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @setTime = (time) ->
        q = $q.defer()
        $http.get("/api/datetime/time/set/#{time}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @syncTime = () ->
        q = $q.defer()
        $http.get("/api/datetime/time/sync").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    return this
