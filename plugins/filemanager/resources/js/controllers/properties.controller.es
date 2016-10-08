angular.module('ajenti.filemanager').controller('FileManagerPropertiesController', function($scope, $routeParams, $location, notify, filesystem, pageTitle, urlPrefix, gettext) {
    pageTitle.set('path', $scope);

    let modeBits = ['ax', 'aw', 'ar', 'gx', 'gw', 'gr', 'ux', 'uw', 'ur', 'sticky', 'setuid', 'setgid'];
    $scope.permissionsDialogVisible = false;

    $scope.path = $routeParams.path;
    $scope.refresh = () =>
        filesystem.stat($scope.path).then((info) => {
            $scope.info = info;
            $scope.mode = {};
            for (let i = 0; i < modeBits.length; i++)
                $scope.mode[modeBits[i]] = !!($scope.info.mode & Math.pow(2, i));
        }, (err) => {
            notify.error(gettext('Could not read file information'), err)
        });

    $scope.hidePermissionsDialog = () => $scope.permissionsDialogVisible = false;

    $scope.applyPermissions = () => {
        $scope.hidePermissionsDialog();

        let mode = 0;
        for (let i = 0; i < modeBits.length; i++) {
            mode += $scope.mode[modeBits[i]] ? Math.pow(2, i) : 0;
        }

        return filesystem.chmod($scope.path, mode).then(() => {
            notify.info(gettext('File mode saved'));
            $scope.refresh();
        });
    };

    $scope.refresh();
});
