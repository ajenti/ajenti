angular.module('ajenti.dns_api').controller('DnsAPIIndexController', function($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('DNS API'));

    $http.get('/api/dns_api/domains').then((resp) => {
        $scope.domains = resp.data;
        $scope.active_domain = resp.data[0]; // Could not exist
        $scope.get_records();
    });

    $scope.get_records = () => {
        $http.get(`/api/dns_api/domain/${$scope.active_domain}/records`).then((rsp) => {
            $scope.records = rsp.data;
        });
    };
});

