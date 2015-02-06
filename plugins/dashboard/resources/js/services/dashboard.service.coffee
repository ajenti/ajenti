angular.module('ajenti.dashboard').service 'dashboard', ($http, $q) ->
    @getAvailableWidgets = () ->
        q = $q.defer()
        $http.get("/api/dashboard/widgets").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @getValues = (data) ->
        q = $q.defer()
        $http.post("/api/dashboard/get-values", data, ignoreLoadingBar: true).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    return this
