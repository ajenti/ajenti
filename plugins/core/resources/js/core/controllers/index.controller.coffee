angular.module('core').controller 'CoreIndexController', ($scope, $location, identity, socket, pageTitle, urlPrefix) -> 
    pageTitle.set('')

    identity.promise.then () ->
        console.log identity.user
        if not identity.user
            location.assign("#{urlPrefix}/view/login/normal")

    $scope.send = () ->
        socket.send('core', 'test message')

    $scope.$on 'socket:core', ($event, data) ->
        console.log data
