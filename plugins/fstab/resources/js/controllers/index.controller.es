angular.module('ajenti.fstab').controller('FstabIndexController', function($scope, $http, pageTitle, gettext, notify, messagebox) {
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

    $scope.show = (device) => {
        $scope.showDetails = true;
        $scope.edit_device = device;
    }

    $scope.save = () => {
        $scope.showDetails = false;
        $http.post('/api/fstab', {config: $scope.fstab}).then( (resp) => {
            notify.success(gettext('Fstab successfully saved!'))
        });
    }

    $scope.remove = (device) => {
        messagebox.show({
            text: gettext('Do you really want to permanently delete this entry?'),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then( () => {
            position = $scope.fstab.indexOf(device);
            $scope.fstab.splice(position, 1);
            $scope.save();
        })
    }

});

