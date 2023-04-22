angular.module('ajenti.dns_api').controller('DnsAPIIndexController', function($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('DNS API'));

    $http.get('/api/dns_api');

});

