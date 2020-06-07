angular.module('ajenti.docker').controller('DockerIndexController', function($scope, $http, $interval, messagebox, pageTitle, gettext, notify) {
    pageTitle.set('Docker');
    $scope.container_stats = [];
    $scope.images= [];
    $scope.ready = false;
    $scope.imagesReady = false;

    $http.get('/api/docker/which').then(() => {
        $scope.getResources();
        $scope.refresh = $interval($scope.getResources, 5000, 0);
    });

    $scope.getResources = () => {
        $http.get('/api/docker/get_resources', {ignoreLoadingBar: true}).then( (resp) => {
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

    $scope.stop = (container) => {
        $http.post('/api/docker/control', {container: container, control:'stop'})
    }

    $scope.start = (container) => {
        $http.post('/api/docker/control', {container: container, control:'start'})
    }

    $scope.remove = (container) => {
        messagebox.show({
            text: gettext('Really remove this container?'),
            positive: gettext('Remove'),
            negative: gettext('Cancel')
        }).then(() => {
            $http.post('/api/docker/control', {container: container, control: 'rm'});
        });
    }

    $scope.getImages = () => {
        $http.post('/api/docker/list_images').then((resp) => {
            $scope.images = resp.data;
            $scope.imagesReady = true;
        });
    }

    $scope.$on('$destroy', () => $interval.cancel($scope.refresh));
});

