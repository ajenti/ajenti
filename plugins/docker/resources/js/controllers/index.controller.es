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
        $http.get('/api/docker/get_resources', {ignoreLoadingBar: true}).then((resp) => {
            $scope.ready = true;
            $scope.container_stats = resp.data;
        });
    }

    $scope.getDetails = (container) => {
        $http.post('/api/docker/get_details', {container: container}).then((resp) => {
            $scope.details = resp.data;
            $scope.showDetails = true;
        });
    }

    $scope.closeDetails = () => $scope.showDetails = false;

    $scope.stop = (container) => {
        $http.post('/api/docker/container_command', {container: container, control:'stop'}).then(() =>
            notify.success(gettext('Stop command successfully sent.')));
    }

    $scope.start = (container) => {
        $http.post('/api/docker/container_command', {container: container, control:'start'}).then(() =>
            notify.success(gettext('Start command successfully sent.')));
    }

    $scope.remove = (container) => {
        messagebox.show({
            text: gettext('Really remove this container?'),
            positive: gettext('Remove'),
            negative: gettext('Cancel')
        }).then(() => {
            $http.post('/api/docker/container_command', {container: container, control: 'rm'}).then(() =>
                notify.success(gettext('Remove command successfully sent.')));
        });
    }

    $scope.getImages = () => {
        $interval.cancel($scope.refresh);
        delete $scope.refresh;
        $http.post('/api/docker/list_images').then((resp) => {
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
            $http.post('/api/docker/remove_image', {image: image}).then(() => {
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

