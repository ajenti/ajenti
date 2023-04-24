angular.module('ajenti.dns_api').controller('DnsAPIIndexController', function($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('DNS API'));
    $scope.detailsVisible = false;

    $scope.supported_types = ['A', 'AAAA', 'ALIAS', 'CNAME', 'MX', 'NS', 'PTR', 'SPF', 'TXT']

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
        $http.get(`/api/dns_api/domain/${$scope.active_domain}/records`).then((resp) => {
            $scope.records = resp.data;
        });
    };

    $scope.openNew = () => {
        $scope.DNSdialog = {
            'type': 'A',
            'ttl': 10800,
            'name': '',
            'value': ''
        };
        $scope.detailsVisible = true;
    };

    $scope.add = () => {
        $http.post(`/api/dns_api/domain/${$scope.active_domain}/records/${$scope.DNSdialog.name}`, {
            'ttl': $scope.DNSdialog.ttl,
            'type': $scope.DNSdialog.type,
            'values': $scope.DNSdialog.value}).then((resp) => {
                code = resp.data[0];
                msg = resp.data[1];
                if (code >= 200 && code < 300) {
                    notify.success(msg);
                    $scope.get_records();
                } else {
                    notify.error(msg);
                }
        });
        $scope.detailsVisible = false;
    };

    $scope.closeDialog = () => $scope.detailsVisible = false;
});

