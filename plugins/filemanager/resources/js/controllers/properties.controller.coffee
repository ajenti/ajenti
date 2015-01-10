angular.module('ajenti.filemanager').controller 'FileManagerPropertiesController', ($scope, $routeParams, $location, notify, filesystem, pageTitle, urlPrefix) -> 
    pageTitle.set('path', $scope)
    
    $scope.path = $routeParams.path
    filesystem.stat($scope.path).then (info) ->
        $scope.info = info
    .catch (err) ->
        notify.error 'Could not read file information', err