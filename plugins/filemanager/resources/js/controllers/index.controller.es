angular.module('ajenti.filemanager').controller('FileManagerIndexController', function($scope, $routeParams, $location, $localStorage, $timeout, notify, identity, filesystem, pageTitle, urlPrefix, tasks, messagebox, $upload, gettext) {
    pageTitle.set('path', $scope);
    $scope.loading = false;
    $scope.newDirectoryDialogVisible = false;
    $scope.newFileDialogVisible = false;
    $scope.clipboardVisible = false;

    $scope.load = (path) => {
        $scope.loading = true;
        return filesystem.list(path).then((data) => {
            $scope.path = path;
            $scope.items = data.items;
            $scope.parent = data.parent;
        }, (data) => {
            notify.error(gettext('Could not load directory'), data.message)
        }).finally(() => {
            $scope.loading = false
        });
    };

    $scope.refresh = () => $scope.load($scope.path);

    $scope.$on('push:filesystem', ($event, msg) => {
        if (msg === 'refresh') {
            $scope.refresh();
        }
    });

    $scope.navigate = path => $location.path(`${urlPrefix}/view/filemanager/${path}`);

    $scope.select = (item) => {
        if (item.isDir) {
            $scope.navigate(item.path);
        } else {
            if ($scope.mode === 'open') {
                $scope.onSelect({item});
            }
            if ($scope.mode === 'save') {
                $scope.name = item.name;
            }
        }
    };

    $scope.clearSelection = () => {
        $scope.items.forEach((item) => item.selected = false)
    };

    $localStorage.fileManagerClipboard = $localStorage.fileManagerClipboard || [];
    $scope.clipboard = $localStorage.fileManagerClipboard;

    $scope.showClipboard = () => $scope.clipboardVisible = true;

    $scope.hideClipboard = () => $scope.clipboardVisible = false;

    $scope.clearClipboard = function() {
        $scope.clipboard.length = 0;
        $scope.hideClipboard();
    };

    $scope.doCut = function() {
        for (let item of $scope.items) {
            if (item.selected) {
                $scope.clipboard.push({
                    mode: 'move',
                    item
                });
            }
        }
        $scope.clearSelection();
    };

    $scope.doCopy = function() {
        for (let item of $scope.items) {
            if (item.selected) {
                $scope.clipboard.push({
                    mode: 'copy',
                    item
                });
            }
        }
        $scope.clearSelection();
    };

    $scope.doDelete = () =>
        messagebox.show({
            text: gettext('Delete selected items?'),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(() => {
            let items = $scope.items.filter((item) => item.selected);
            tasks.start('aj.plugins.filesystem.tasks.Delete', [], {items});
            $scope.clearSelection();
        })
    ;

    $scope.doPaste = function() {
        let items = angular.copy($scope.clipboard);
        tasks.start(
            'aj.plugins.filesystem.tasks.Transfer',
            [],
            {destination: $scope.path, items}
        ).then(() => {
            $scope.clearClipboard()
        });
    };

    // new file dialog

    $scope.showNewFileDialog = function() {
        $scope.newFileName = '';
        $scope.newFileDialogVisible = true;
    };

    $scope.doCreateFile = function() {
        if (!$scope.newFileName) {
            return;
        }

        return filesystem.createFile($scope.path + '/' + $scope.newFileName).then(() => {
            $scope.refresh();
            $scope.newFileDialogVisible = false;
        }, (err) => {
            notify.error(gettext('Could not create file'), err.message)
        });
    };

    // new directory dialog

    $scope.showNewDirectoryDialog = function() {
        $scope.newDirectoryName = '';
        $scope.newDirectoryDialogVisible = true;
    };

    $scope.doCreateDirectory = function() {
        if (!$scope.newDirectoryName) {
            return;
        }

        return filesystem.createDirectory($scope.path + '/' + $scope.newDirectoryName).then(() => {
            $scope.refresh();
            $scope.newDirectoryDialogVisible = false;
        }, (err) => {
            notify.error(gettext('Could not create directory'), err.message)
        });
    };

    // upload dialog
    $scope.uploadFiles = [];
    $scope.uploadPending = [];

    $scope.showUploadDialog = () => $scope.uploadDialogVisible = true;

    let uploadCallback = () => {
        if ($scope.uploadPending.length > 0) {
            $scope.uploadCurrent = {
                file: $scope.uploadPending[0],
                name: $scope.uploadPending[0].name
            };
            $scope.uploadPending.remove($scope.uploadCurrent.file);
            $upload.upload({
                url: `${urlPrefix}/api/filesystem/upload/${$scope.path}/${$scope.uploadCurrent.name}`,
                file: $scope.uploadCurrent.file,
                fileName: $scope.uploadCurrent.name,
                fileFormDataName: 'upload'
            }).success(() => {
                notify.success(gettext('Uploaded'), $scope.uploadCurrent.name);
                $scope.refresh();
                return uploadCallback();
            })
            .xhr(xhr =>
                $scope.uploadCurrent.cancel = () => xhr.abort()
            )
            .progress((e) => {
                $scope.uploadCurrent.length = e.total;
                $scope.uploadCurrent.progress = e.loaded;
            })
            .error((e) => {
                if ($scope.uploadCurrent) {
                    notify.error(gettext('Upload failed'), $scope.uploadCurrent.name);
                    uploadCallback();
                } else {
                    notify.info(gettext('Upload cancelled'));
                }
            });
        } else {
            $scope.uploadDialogVisible = false;
            $scope.uploadPending = [];
            $scope.uploadRunning = false;
            $scope.uploadCurrent = null;
        }
    };

    $scope.doUpload = () =>
        $timeout(() => {
            $scope.uploadRunning = true;
            $scope.uploadPending = $scope.uploadFiles;
            $scope.uploadFiles = [];
            uploadCallback();
        });

    $scope.cancelUpload = () => {
        $scope.uploadDialogVisible = false;
        $scope.uploadFiles = [];
        $scope.uploadPending = [];
        $scope.uploadRunning = false;
        if ($scope.uploadCurrent) {
            $scope.uploadCurrent.cancel();
            $scope.uploadCurrent = null;
        }
    };

    // ---

    identity.promise.then(() => {
        let root = identity.profile.fs_root || '/';
        let path = $routeParams.path || '/';
        if (path.indexOf(root) !== 0) {
            path = root;
        }

        if ($routeParams.path) {
            $scope.load(path);
        } else {
            $scope.navigate(root);
        }
    });
});
