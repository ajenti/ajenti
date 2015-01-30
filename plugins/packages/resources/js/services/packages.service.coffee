angular.module('ajenti.packages').service 'packages', ($http, $q) ->
    @getManagers = () ->
        q = $q.defer()
        $http.get("/api/packages/managers").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @list = (managerId, query) ->
        q = $q.defer()
        $http.get("/api/packages/list/#{managerId}?query=#{query}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @get = (managerId, packageId) ->
        q = $q.defer()
        $http.get("/api/packages/get/#{managerId}/#{packageId}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @updateLists = (managerId) ->
        q = $q.defer()
        $http.get("/api/packages/update-lists/#{managerId}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    return this
