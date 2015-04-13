angular.module('core').controller 'CoreLoginController', ($scope, $log, $rootScope, $routeParams, identity, notify) ->
    $rootScope.disableExpiredSessionInterceptor = true
    $scope.working = false
    $scope.success = false

    if $routeParams.mode.indexOf('sudo:') == 0
        $scope.mode = 'sudo'
        $scope.username = $routeParams.mode.split(':')[1]
    else
        $scope.mode = $routeParams.mode

    $scope.login = () ->
        if not $scope.username or not $scope.password
            return
        $scope.working = true
        identity.auth($scope.username, $scope.password, $scope.mode).then (username) ->
            $scope.success = true
            location.href = $routeParams.nextPage or '/'
        .catch (error) ->
            $scope.working = false
            $log.log 'Authentication failed', error
            notify.error 'Authentication failed', error

    setTimeout () ->
        s = document.createElement('script')
        s.src = 'https://login.persona.org/include.js'
        $('head').append(s)

    $scope.personaLogin = () ->
        navigator.id.watch {
            onlogin: (assertion) ->
                $scope.working = true
                identity.personaAuth(assertion, location.href).then (username) ->
                    $scope.success = true
                    notify.success 'Authentication succeeded', username
                    location.href = $routeParams.nextPage or '/'
                .catch (err) ->
                    $scope.working = false
                    notify.error 'Authentication failed', err
                    navigator.id.logout()
            onlogout: () -> null
        }
        navigator.id.request {
            siteName: identity.machine.name
            backgroundColor: '#678'
        }
