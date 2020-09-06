angular.module('ajenti.fstab').controller('FstabIndexController', function($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Fstab'));

    $scope.showDetails = false;

    $http.get('/api/get_mounted').then( (resp) => {
	    $scope.mounted = resp.data;
    });

    $scope.umount = (entry) => {
        $http.post('/api/umount', {mountpoint: entry.mountpoint}).then( (resp) => {
            notify.success(gettext('Device successfully unmounted!'));
            position = $scope.mounted.indexOf(entry);
            $scope.mounted.splice(position, 1);
        });
    }

    $http.get('/api/fstab').then( (resp) => {
	    $scope.fstab = resp.data.filesystems;
    });

    $http.post('/api/fstab', {my_var: 'fstab'}).then( (resp) => {
	    $scope.python_post = resp.data;
    });

    $scope.show = (device) => {
        $scope.showDetails = true;
        $scope.edit_device = device;
    }
});

