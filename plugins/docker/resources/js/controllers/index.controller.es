angular.module('ajenti.docker').controller('DockerIndexController', function($scope, $http, $interval, messagebox, pageTitle, gettext, notify) {
    pageTitle.set('Docker');
    $scope.container_stats = [];
    $scope.images= [];
    $scope.ready = false;
    $scope.imagesReady = false;

    $http.get('/api/docker/which').then(() => {
            $scope.getResources();
            $scope.start_refresh();
            $scope.installed = true;
        }
        , (err) => {
            $scope.ready = true;
            $scope.installed = false;
        }
    );

    $scope.start_refresh = () => {
        if ($scope.refresh === undefined)
            $scope.refresh = $interval($scope.getResources, 5000, 0);
    }
    $scope.getResources = () => {
        $http.get('/api/docker/containers', {ignoreLoadingBar: true}).then((resp) => {
            $scope.ready = true;
            $scope.container_stats = resp.data;
        });
    }

    $scope.getDetails = (container_id) => {
        $http.get(`/api/docker/container/${container_id}`).then((resp) => {
            $scope.details = resp.data;
            $scope.showDetails = true;
        });
    }

    $scope.closeDetails = () => $scope.showDetails = false;

    $scope.stop = (container_id) => {
        $http.post('/api/docker/container_command', {container_id: container_id, control:'stop'}).then(() =>
            notify.success(gettext('Stop command successfully sent.')));
    }

    $scope.start = (container_id) => {
        $http.post('/api/docker/container_command', {container_id: container_id, control:'start'}).then(() =>
            notify.success(gettext('Start command successfully sent.')));
    }

    $scope.remove = (container_id) => {
        messagebox.show({
            text: gettext('Really remove this container?'),
            positive: gettext('Remove'),
            negative: gettext('Cancel')
        }).then(() => {
            $http.post('/api/docker/container_command', {container_id: container_id, control: 'rm'}).then(() =>
                notify.success(gettext('Remove command successfully sent.')));
        });
    }

    $scope.getImages = () => {
        $interval.cancel($scope.refresh);
        delete $scope.refresh;
        $http.get('/api/docker/images').then((resp) => {
            $scope.images = resp.data;console.log($scope.images);
            $scope.imagesReady = true;
        });
    }

    $scope.removeImage = (image) => {
        messagebox.show({
            text: gettext('Really remove this image?'),
            positive: gettext('Remove'),
            negative: gettext('Cancel')
        }).then(() => {
            $http.delete(`/api/docker/image/${image}`).then(() => {
                notify.success(gettext('Remove command successfully sent.'));
                for (let i = 0; i < $scope.images.length; i++) {
                    if ($scope.images[i].hash == image)
                        $scope.images.splice(i, 1);
                }
            },
            (err) =>
                notify.error(err.data.message)
            );
        })};

    $scope.$on('$destroy', () => $interval.cancel($scope.refresh));
});

