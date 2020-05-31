angular.module('check_certificates').controller('CertWidgetController', ($scope, $http, config) =>
    $scope.$on('widget-update', function($event, id, data) {
        if (id !== $scope.widget.id) {
            return;
        }

        $scope.status = []

        if (data) {

            config.getUserConfig().then((userConfig) => {
                $scope.userConfig = userConfig;

                for (let url of $scope.userConfig.certificates.domain) {
                    $http.post('/api/check_cert/test', {url: url}).then((resp) => {
                        if (resp.data.status == 'danger' || resp.data.status == 'warning')
                            $scope.status.push(resp.data);
                    });
                }
            });
        }

    })
);

