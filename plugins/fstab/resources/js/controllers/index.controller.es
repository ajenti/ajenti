angular.module('ajenti.fstab').controller('FstabIndexController', function($scope, $http, pageTitle, gettext, notify, messagebox) {
    pageTitle.set(gettext('Fstab'));

    $scope.showDetails = false;
    $scope.add_new = false;

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

    $scope.edit = (device) => {
        $scope.edit_device = device;
        $scope.showDetails = true;
    }

    $scope.save = () => {
        $scope.showDetails = false;
        $http.post('/api/fstab', {config: $scope.fstab}).then( (resp) => {
            notify.success(gettext('Fstab successfully saved!'))
        });
    }

    $scope.add = () => {
        $scope.add_new = true;
        $scope.edit_device = {
            'device': '',
            'mountpoint': '/',
            'type': 'ext4',
            'options': 'defaults',
            'freq': '0',
            'passno': '0',
        };
        $scope.showDetails = true;
    }

    $scope.saveNew = () => {
        $scope.reset()
        $scope.fstab.push($scope.edit_device);
        $scope.save();
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

    $scope.reset = () => {
        $scope.showDetails = false;
        $scope.add_new = false;
    }
});

