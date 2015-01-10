angular.module('ajenti.filemanager').controller 'FileManagerIndexController', ($scope, $routeParams, $location, notify, filesystem, pageTitle, urlPrefix) -> 
    pageTitle.set('path', $scope)
    $scope.loading = false

    $scope.load = (path) ->
        $scope.loading = true
        filesystem.list(path).then (data) ->
            $scope.path = path
            $scope.items = data.items
            $scope.parent = data.parent
        .catch () ->
            notify.error 'Could not load directory'
        .finally () ->
            $scope.loading = false

    $scope.navigate = (path) ->
        $location.path("#{urlPrefix}/view/filemanager/#{path}")

    $scope.select = (item) ->
        if item.isDir
            $scope.navigate(item.path)
        else
            if $scope.mode == 'open'
                $scope.onSelect({item: item})
            if $scope.mode == 'save'
                $scope.name = item.name

    $scope.clearSelection = () ->
        for item in $scope.items
            item.selected = false

    $scope.doCut = () ->
        for item in $scope.items
            ;
        $scope.clearSelection()

    $scope.doCopy = () ->
        for item in $scope.items
            ;
        $scope.clearSelection()

    $scope.doDelete = () ->
        for item in $scope.items
            ;
        $scope.clearSelection()

    if $routeParams.path
        $scope.load($routeParams.path)
    else
        $scope.navigate('/')
