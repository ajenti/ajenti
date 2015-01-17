angular.module('ajenti.filemanager').controller 'FileManagerIndexController', ($scope, $routeParams, $location, $localStorage, notify, filesystem, pageTitle, urlPrefix) -> 
    pageTitle.set('path', $scope)
    $scope.loading = false
    $scope.newDirectoryDialogVisible = false
    $scope.newFileDialogVisible = false
    $scope.clipboardVisible = false

    $scope.load = (path) ->
        $scope.loading = true
        filesystem.list(path).then (data) ->
            $scope.path = path
            $scope.items = data.items
            $scope.parent = data.parent
        .catch (data) ->
            notify.error 'Could not load directory', data.message
        .finally () ->
            $scope.loading = false

    $scope.refresh = () ->
        $scope.load($scope.path)

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

    if not $localStorage.fileManagerClipboard
        $localStorage.fileManagerClipboard = []
    $scope.clipboard = $localStorage.fileManagerClipboard

    $scope.showClipboard = () ->
        $scope.clipboardVisible = true

    $scope.hideClipboard = () ->
        $scope.clipboardVisible = false

    $scope.clearClipboard = () ->
        $scope.clipboard.length = 0
        $scope.hideClipboard()

    $scope.doCut = () ->
        for item in $scope.items
            if item.selected
                $scope.clipboard.push {
                    mode: 'move'
                    item: item
                }
        $scope.clearSelection()

    $scope.doCopy = () ->
        for item in $scope.items
            if item.selected
                $scope.clipboard.push {
                    mode: 'copy'
                    item: item
                }
        $scope.clearSelection()

    $scope.doDelete = () ->
        if confirm('Delete selected items?')
            for item in $scope.items
                if item.selected
                    ;
            $scope.clearSelection()

    # NewFileDialog

    $scope.showNewFileDialog = () ->
        $scope.newFileName = ''
        $scope.newFileDialogVisible = true

    $scope.doCreateFile = () ->
        if not $scope.newFileName
            return

        filesystem.createFile($scope.path + '/' + $scope.newFileName).then () ->
            $scope.refresh()
            $scope.hideNewFileDialog()
        .catch (err) ->
            notify.error 'Could not create file', err.message

    $scope.hideNewFileDialog = () ->    
        $scope.newFileDialogVisible = false

    # NewDirectoryDialog
    
    $scope.showNewDirectoryDialog = () ->
        $scope.newDirectoryName = ''
        $scope.newDirectoryDialogVisible = true

    $scope.doCreateDirectory = () ->
        if not $scope.newDirectoryName
            return

        filesystem.createDirectory($scope.path + '/' + $scope.newDirectoryName).then () ->
            $scope.refresh()
            $scope.hideNewDirectoryDialog()
        .catch (err) ->
            notify.error 'Could not create directory', err.message

    $scope.hideNewDirectoryDialog = () ->    
        $scope.newDirectoryDialogVisible = false

    # ---

    if $routeParams.path
        $scope.load($routeParams.path)
    else
        $scope.navigate('/')
