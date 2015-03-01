angular.module('core').controller 'CoreIndexController', ($scope, $location, $http, identity, socket, pageTitle, urlPrefix, tasks) ->
    pageTitle.set('')

    $location.path('/view/dashboard')

    identity.promise.then () ->
        console.log identity.user
        if not identity.user
            location.assign("#{urlPrefix}/view/login/normal")

    $scope.send = () ->
        #$http.get('/testtasks')
        tasks.start 'aj.plugins.core.views.main.MyTask', ['arg'], {kw:'arg'}
        socket.send('core', 'test message')

    $scope.boom = () ->
        $http.get('/boom')

    $scope.$on 'socket:core', ($event, data) ->
        console.log data
