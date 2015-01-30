angular.module('ajenti.packages').service 'packages', ($http, $q, tasks) ->
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
        tasks.start('aj.plugins.packages.tasks.UpdateLists', [], manager_id: managerId).then (data) ->
            q.resolve(data)
        .catch (err) ->
            q.reject(err)
        return q.promise

    @applySelection = (managerId, selection) ->
        q = $q.defer()
        $http.post("/api/packages/apply/#{managerId}", selection).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    return this
