angular.module('ajenti.augeas').service 'augeas', ($http, $q, AugeasConfig) ->
    @get = (endpoint) ->
        q = $q.defer()
        $http.get("/api/augeas/endpoint/get/#{endpoint}").success (data) ->
            q.resolve(AugeasConfig.get(data))
        .error (err) ->
            q.reject(err)
        return q.promise

    @set = (endpoint, config) ->
        q = $q.defer()
        $http.post("/api/augeas/endpoint/set/#{endpoint}", config.serialize()).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    return this
