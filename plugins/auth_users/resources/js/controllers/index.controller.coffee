angular.module('ajenti.auth.users').controller 'AuthUsersIndexController', ($scope, $http, notify, pageTitle, settings, passwd) ->
    pageTitle.set('Users')

    settings.getConfig().then (data) ->
        $scope.config = data
    .catch () ->
        $scope.config = {}
        notify.error 'Could not load config'

    $scope.removeUser = (username) ->
        delete $scope.config.auth_users[username]

    passwd.list().then (l) ->
        $scope.systemUsers = l

        $scope.getSystemUser = (uid) ->
            for u in $scope.systemUsers
                if u.uid == uid
                    return u

    $scope.save = () ->
        settings.setConfig($scope.config).then () ->
            notify.success 'Saved'

    $scope.setPassword = (username, password) ->
        settings.setConfig($scope.config).then () ->
            $http.post("/api/auth-users/set-password/#{username}", password).then () ->
                notify.success 'Password updated'
                settings.getConfig().then (data) ->
                    $scope.config = data

    $scope.addUser = (username) ->
        $scope.config.auth_users[username] = {uid: 0}
        $scope.newUsername = ''

    $scope.isDangerousSetup = () ->
        if not $scope.config
            return
        safe = false
        for username of $scope.config.auth_users
            if $scope.config.auth_users[username].uid == 0
                safe = true
        return not safe
