angular.module('ajenti.services').service 'services', ($http, $q) ->
    @getManagers = () ->
        q = $q.defer()
        $http.get("/api/services/managers").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @getServices = (managerId) ->
        q = $q.defer()
        $http.get("/api/services/list/#{managerId}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @getService = (managerId, serviceId) ->
        q = $q.defer()
        $http.get("/api/services/get/#{managerId}/#{serviceId}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @runOperation = (service, operation) ->
        q = $q.defer()
        $http.get("/api/services/do/#{operation}/#{service.managerId}/#{service.id}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    return this
