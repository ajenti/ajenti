angular.module('ajenti.passwd').service 'passwd', ($http, $q) ->
    @list = () ->
        q = $q.defer()
        $http.get("/api/passwd/list").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    return this
