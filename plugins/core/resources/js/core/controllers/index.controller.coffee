angular.module('core').controller 'CoreIndexController', ($scope, $location, $http, identity, socket, pageTitle, urlPrefix) -> 
    pageTitle.set('')

    identity.promise.then () ->
        console.log identity.user
        if not identity.user
            location.assign("#{urlPrefix}/view/login/normal")

    $scope.send = () ->
        $http.get('/testtasks')
        socket.send('core', 'test message')

    $scope.$on 'socket:core', ($event, data) ->
        console.log data
