angular.module('ajenti.check_certificates').config($routeProvider => {
    $routeProvider.when('/view/check_cert/certificates', {
        templateUrl: '/check_certificates:resources/partial/index.html',
        controller: 'CertIndexController'
    })
});
