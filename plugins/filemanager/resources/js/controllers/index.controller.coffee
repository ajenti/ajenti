angular.module('ajenti.filemanager').controller 'FileManagerIndexController', ($scope, $routeParams, $location, $localStorage, $timeout, notify, filesystem, pageTitle, urlPrefix, tasks, messagebox, $upload) ->
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

    $scope.$on 'push:filesystem', ($event, msg) ->
        if msg == 'refresh'
            $scope.refresh()

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
        messagebox.show(text: 'Delete selected items?', positive: 'Delete', negative: 'Cancel').then () ->
            items = (item for item in $scope.items when item.selected)
            tasks.start('aj.plugins.filesystem.tasks.Delete', [], items: items)
            $scope.clearSelection()

    $scope.doPaste = () ->
        items = angular.copy($scope.clipboard)
        tasks.start('aj.plugins.filesystem.tasks.Transfer', [], destination: $scope.path, items: items).then () ->
            $scope.clearClipboard()

    # new file dialog

    $scope.showNewFileDialog = () ->
        $scope.newFileName = ''
        $scope.newFileDialogVisible = true

    $scope.doCreateFile = () ->
        if not $scope.newFileName
            return

        filesystem.createFile($scope.path + '/' + $scope.newFileName).then () ->
            $scope.refresh()
            $scope.newFileDialogVisible = false
        .catch (err) ->
            notify.error 'Could not create file', err.message

    # new directory dialog

    $scope.showNewDirectoryDialog = () ->
        $scope.newDirectoryName = ''
        $scope.newDirectoryDialogVisible = true

    $scope.doCreateDirectory = () ->
        if not $scope.newDirectoryName
            return

        filesystem.createDirectory($scope.path + '/' + $scope.newDirectoryName).then () ->
            $scope.refresh()
            $scope.newDirectoryDialogVisible = false
        .catch (err) ->
            notify.error 'Could not create directory', err.message

    # upload dialog
    $scope.uploadFiles = []
    $scope.uploadPending = []

    $scope.showUploadDialog = () ->
        $scope.uploadDialogVisible = true

    uploadCallback = () ->
        if $scope.uploadPending.length > 0
            $scope.uploadCurrent = {
                file: $scope.uploadPending[0]
                name: $scope.uploadPending[0].name
            }
            $scope.uploadPending.remove($scope.uploadCurrent.file)
            $upload.upload({
                url: "#{urlPrefix}/api/filesystem/upload/#{$scope.path}/#{$scope.uploadCurrent.name}"
                file: $scope.uploadCurrent.file
                fileName: $scope.uploadCurrent.name
                fileFormDataName: 'upload'
            }).success () ->
                notify.success 'Uploaded', $scope.uploadCurrent.name
                $scope.refresh()
                uploadCallback()
            .xhr (xhr) ->
                $scope.uploadCurrent.cancel = () ->
                    xhr.abort()
            .progress (e) ->
                $scope.uploadCurrent.length = e.total
                $scope.uploadCurrent.progress = e.loaded
            .error (e) ->
                if $scope.uploadCurrent
                    notify.error 'Upload failed', $scope.uploadCurrent.name
                    uploadCallback()
                else
                    notify.info 'Upload cancelled'
        else
            $scope.uploadDialogVisible = false
            $scope.uploadPending = []
            $scope.uploadRunning = false
            $scope.uploadCurrent = null

    $scope.doUpload = () ->
        $timeout () ->
            $scope.uploadRunning = true
            $scope.uploadPending = $scope.uploadFiles
            $scope.uploadFiles = []
            uploadCallback()

    $scope.cancelUpload = () ->
        $scope.uploadDialogVisible = false
        $scope.uploadFiles = []
        $scope.uploadPending = []
        $scope.uploadRunning = false
        if $scope.uploadCurrent
            $scope.uploadCurrent.cancel()
            $scope.uploadCurrent = null

    # ---

    if $routeParams.path
        $scope.load($routeParams.path)
    else
        $scope.navigate('/')
