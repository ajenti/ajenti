angular.module('core').service 'identity', ($http, $location, $timeout, $q) ->
    @init = () ->
        q = $q.defer()
        @promise = q.promise
        $http.get('/api/core/identity').success (data) =>
            @user = data.identity.user
            @effective = data.identity.effective
            @machine = data.machine
            @isSuperuser = @user == 'root'
            q.resolve()
        .error () ->
            q.reject()

    @init()

    @auth = (username, password, mode) ->
        q = $q.defer()
        
        data = {
            username: username
            password: password
            mode: mode
        }
        $http.post('/api/core/auth', data).success (data) ->
            if data.success
                q.resolve(data.username)
            else
                q.reject(data.error)
        .error () ->
            q.reject()

        return q.promise

    @personaAuth = (assertion, audience) ->
        q = $q.defer()
        
        data = {
            assertion: assertion
            audience: audience
            mode: 'persona'
        }
        $http.post('/api/core/auth', data).success (data) ->
            if data.success
                q.resolve(data.username)
            else
                q.reject(data.error)
        .error () ->
            q.reject()

        return q.promise

    @login = () ->
        location.assign("/view/login/normal/#{$location.path()}")

    @elevate = () ->
        $http.get('/api/core/logout')
        $timeout () =>
            location.href = "/view/login/sudo:#{@user}/#{$location.path()}"
        , 1000

    @logout = () ->
        $http.get('/api/core/logout')
        $timeout () ->
            location.assign("/view/login/normal/#{$location.path()}")
        , 1000

    return this
