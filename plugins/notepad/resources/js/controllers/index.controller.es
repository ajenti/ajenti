angular.module('ajenti.notepad').controller('NotepadIndexController', function($scope, $routeParams, $location, notify, filesystem, pageTitle, hotkeys, config, gettext) {
    pageTitle.set('');

    $scope.newFile = () => {
        if ($scope.content) {
            if (!confirm(gettext('Current file will be closed. Continue?'))) {
                return;
            }
        }
        $scope.path = null;
        $scope.content = '';
    };

    $scope.showOpenDialog = () => $scope.openDialogVisible = true;

    $scope.open = (path) => {
        let url = `/view/notepad/${path}`;
        if ($location.path() !== url) {
            $location.path(url);
            return;
        }

        $scope.openDialogVisible = false;
        $scope.path = path;
        pageTitle.set(path);

        return filesystem.read($scope.path).then((content) => {
            $scope.content = content;
            $scope.$broadcast('ace:reload', $scope.path);
        }, err => {
            notify.error(gettext('Could not open the file'), err.message)
        });
    };

    $scope.save = () => $scope.saveAs($scope.path);

    $scope.saveAs = (path) => {
        $scope.saveDialogVisible = false;
        let mustReload = path !== $scope.path;
        $scope.path = path;
        return filesystem.write($scope.path, $scope.content).then(() => {
            notify.success('Saved', $scope.path);
            if (mustReload) {
                return $scope.open($scope.path);
            } else {
                $scope.$broadcast('ace:reload', $scope.path);
            }
        }, err => {
            notify.error(gettext('Could not save the file'), err.message)
        });
    };

    $scope.showSaveDialog = () => {
        $scope.saveDialogVisible = true;
        if ($scope.path) {
            let t = $scope.path.split('/');
            $scope.saveAsName = t[t.length - 1];
        } else {
            $scope.saveAsName = 'new.txt';
        }
    };

    config.getUserConfig().then((userConfig) => {
        $scope.userConfig = userConfig;
        $scope.userConfig.notepad = $scope.userConfig.notepad || {};
        $scope.userConfig.notepad.bookmarks = $scope.userConfig.notepad.bookmarks || [];
        $scope.bookmarks = $scope.userConfig.notepad.bookmarks;
    });

    $scope.toggleBookmark = () => {
        $scope.bookmarks.toggleItem($scope.path)
        config.setUserConfig($scope.userConfig);
    };

    if ($routeParams.path) {
        $scope.open($routeParams.path);
    } else {
        $scope.newFile();
    }

    hotkeys.on($scope, (key, event) => {
        if (key === 'O' && event.ctrlKey) {
            $scope.showOpenDialog();
            return true;
        }
        if (key === 'S' && event.ctrlKey) {
            if ($scope.path && !event.shiftKey) {
                $scope.save();
            } else {
                $scope.showSaveDialog();
            }
            return true;
        }
        if (key === 'N' && event.ctrlKey) {
            $scope.newFile();
            return true;
        }
        return false;
    });
});
