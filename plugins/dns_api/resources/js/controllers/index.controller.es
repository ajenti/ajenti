angular.module('ajenti.dns_api').controller('DnsAPIIndexController', function($scope, $http, pageTitle, gettext, notify, messagebox) {
    pageTitle.set(gettext('DNS API'));
    $scope.detailsVisible = false;

    $scope.supported_types = ['A', 'AAAA', 'ALIAS', 'CNAME', 'MX', 'NS', 'PTR', 'SPF', 'TXT']

    $http.get('/api/dns_api/domains').then((resp) => {
        $scope.domains = resp.data[0];
        $scope.provider = resp.data[1];
        if ($scope.domains.length > 0) {
            $scope.domains.active = $scope.domains[0];
            $scope.get_records();
        } else {
            $scope.domains.active = '';
        }
    });

    $scope.get_records = () => {
        $http.get(`/api/dns_api/domain/${$scope.domains.active}/records`).then((resp) => {
            $scope.records = resp.data;
        });
    };

    $scope.openDialog = (record) => {
        if (record) {
            $scope.DNSdialog = {
                'type': record.type,
                'ttl': record.ttl,
                'name': record.name,
                'value': record.values.join(' '),
                'mode': 'update'
            };
        } else {
            $scope.DNSdialog = {
                'type': 'A',
                'ttl': 10800,
                'name': '',
                'value': '',
                'mode': 'add'
            };
        }
        $scope.detailsVisible = true;
    };

    $scope.add = () => {
        $http.post(`/api/dns_api/domain/${$scope.domains.active}/records/${$scope.DNSdialog.name}`, {
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

    $scope.update = () => {
        $http.put(`/api/dns_api/domain/${$scope.domains.active}/records/${$scope.DNSdialog.name}`, {
            'ttl': $scope.DNSdialog.ttl,
            'type': $scope.DNSdialog.type,
            'values': $scope.DNSdialog.value}).then((resp) => {
                code = resp.data[0];
                msg = resp.data[1];
                if (code >= 200 && code < 300) {
                    notify.success(msg);
                    $scope.get_records();
                } else {
                    console.log(msg);
                    notify.error(msg);
                }
        });
        $scope.detailsVisible = false;
    };

    $scope.delete = (record) => {
        messagebox.show({
            text: gettext(`Really delete the entry "${record.name} ${record.type} ${record.values}"?`),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(() => {
            $http.delete(`/api/dns_api/domain/${$scope.domains.active}/records/${record.type}/${record.name}`).then((resp) => {
                code = resp.data[0];
                msg = resp.data[1];
                if (code >= 200 && code < 300) {
                    notify.success(msg);
                    $scope.get_records();
                } else {
                    notify.error(msg);
                }
            });
        });
    }

    $scope.closeDialog = () => $scope.detailsVisible = false;
});

