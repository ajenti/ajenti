angular.module('ajenti.notepad').controller 'NotepadIndexController', ($scope, $routeParams, $location, notify, filesystem, pageTitle, hotkeys, urlPrefix) ->
    pageTitle.set('')

    $scope.newFile = () ->
        if $scope.content
            if not confirm('Current file will be closed. Continue?')
                return
        $scope.path = null
        $scope.content = ''

    $scope.showOpenDialog = () ->
        $scope.openDialogVisible = true

    $scope.open = (path) ->
        url = "#{urlPrefix}/view/notepad/#{path}"
        if $location.path() != url
            $location.path(url)
            return

        $scope.openDialogVisible = false
        $scope.path = path
        pageTitle.set(path)

        filesystem.read($scope.path).then (content) ->
            $scope.content = content
            $scope.$broadcast 'ace:reload', $scope.path
        .catch (err) ->
            notify.error 'Could not open the file', err.message

    $scope.save = () ->
        $scope.saveAs($scope.path)

    $scope.saveAs = (path) ->
        $scope.saveDialogVisible = false
        mustReload = path != $scope.path
        $scope.path = path
        filesystem.write($scope.path, $scope.content).then () ->
            notify.success 'Saved', $scope.path
            if mustReload
                $scope.open($scope.path)
            else
                $scope.$broadcast 'ace:reload', $scope.path
        .catch (err) ->
            notify.error 'Could not save the file', err.message

    $scope.showSaveDialog = () ->
        $scope.saveDialogVisible = true
        if $scope.path
            t = $scope.path.split('/')
            $scope.saveAsName = t[t.length - 1]
        else
            $scope.saveAsName = 'new.txt'

    if $routeParams.path
        $scope.open($routeParams.path)
    else
        $scope.newFile()

    hotkeys.on $scope, (key, event) ->
        if key == 'O' and event.ctrlKey
            $scope.showOpenDialog()
            return true
        if key == 'S' and event.ctrlKey
            if $scope.path and not event.shiftKey
                $scope.save()
            else
                $scope.showSaveDialog()
            return true
        if key == 'N' and event.ctrlKey
            $scope.newFile()
            return true
        return false
