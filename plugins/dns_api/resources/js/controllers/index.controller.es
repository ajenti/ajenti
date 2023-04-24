angular.module('ajenti.dns_api').controller('DnsAPIIndexController', function($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('DNS API'));

    $http.get('/api/dns_api/domains').then((resp) => {
        $scope.domains = resp.data;
        if ($scope.domains.length > 0) {
            $scope.active_domain = resp.data[0];
            $scope.get_records();
        } else {
            $scope.active_domain = '';
        }
    });

    $scope.get_records = () => {
        $http.get(`/api/dns_api/domain/${$scope.active_domain}/records`).then((rsp) => {
            $scope.records = rsp.data;
        });
    };
});

