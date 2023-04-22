angular.module('ajenti.dns_api').config(($routeProvider) => {
    $routeProvider.when('/view/dns_api', {
        templateUrl: '/dns_api:resources/partial/index.html',
        controller: 'DnsAPIIndexController',
    });
});
