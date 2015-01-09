angular.module('core').controller 'CoreIndexController', ($scope, $location, identity, socket, pageTitle) -> 
    pageTitle.set('')

    identity.promise.then () ->
        console.log identity.user
        if not identity.user
            $location.path('/view/login')

    $scope.send = () ->
        socket.send('core', 'test message')

    $scope.$on 'socket:core', ($event, data) ->
        console.log data
