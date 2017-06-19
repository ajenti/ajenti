angular.module('ajenti.filemanager').controller('FileManagerIndexController', function($scope, $routeParams, $location, $localStorage, $timeout, notify, identity, filesystem, pageTitle, urlPrefix, tasks, messagebox, gettext) {
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

    $scope.onUploadBegin = async ($flow) => {
        msg = messagebox.show({progress: true})
        filesystem.startFlowUpload($flow, $scope.path).then(() => {
            notify.success(gettext('Uploaded'))
            $scope.refresh()
            msg.close()
        }, null, (progress) => {
          console.log(progress)
            msg.messagebox.title = `Uploading: ${Math.floor(100 * progress)}%`
        })
    }

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
