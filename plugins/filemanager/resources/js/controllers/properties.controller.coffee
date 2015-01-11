angular.module('ajenti.filemanager').controller 'FileManagerPropertiesController', ($scope, $routeParams, $location, notify, filesystem, pageTitle, urlPrefix) -> 
    pageTitle.set('path', $scope)

    $scope.permissionsDialogVisible = false
    modeBits = ['ax', 'aw', 'ar', 'gx', 'gw', 'gr', 'ux', 'uw', 'ur', 'sticky', 'setuid', 'setgid']
    
    $scope.path = $routeParams.path
    $scope.refresh = () ->
        filesystem.stat($scope.path).then (info) ->
            $scope.info = info
            $scope.mode = {}
            for i in [0...modeBits.length]
                $scope.mode[modeBits[i]] = !!($scope.info.mode & Math.pow(2, i))
        .catch (err) ->
            notify.error 'Could not read file information', err

    $scope.hidePermissionsDialog = () ->
        $scope.permissionsDialogVisible = false

    $scope.applyPermissions = () ->
        $scope.hidePermissionsDialog()
        
        mode = 0
        for i in [0...modeBits.length]
            mode += if $scope.mode[modeBits[i]] then Math.pow(2, i) else 0
        
        filesystem.chmod($scope.path, mode).then () ->
            notify.info 'Applied'
            $scope.refresh()

    $scope.refresh()