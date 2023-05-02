angular.module('core').config(($routeProvider, $locationProvider, urlPrefix) => {
    $locationProvider.html5Mode({enabled: true, requireBase: false});

    $routeProvider.originalWhen = $routeProvider.when;
    $routeProvider.when = (url, config) => {
        url = urlPrefix + url;
        return $routeProvider.originalWhen(url, config);
    };

    $routeProvider.when('/view/', {
        templateUrl: '/core:resources/partial/index.html',
        controller: 'CoreIndexController'
    });

    $routeProvider.when('/view/login/:mode', {
        templateUrl: '/core:resources/partial/login.html',
        controller: 'CoreLoginController'
    });

    $routeProvider.when('/view/login/:mode/:nextPage*', {
        templateUrl: '/core:resources/partial/login.html',
        controller: 'CoreLoginController'
    });

    $routeProvider.when('/view/reset_password_send', {
        templateUrl: '/core:resources/partial/reset_password_send.html',
        controller: 'CorePWResetMailController'
    });

    $routeProvider.when('/view/reset_password/:serial', {
        templateUrl: '/core:resources/partial/reset_password.html',
        controller: 'CorePWResetController'
    });

    $routeProvider.when('/view/ui-test', {
        templateUrl: '/core:resources/partial/index.html'
    });

    $routeProvider.when('/view/totp', {
        templateUrl: '/core:resources/partial/totp.html',
        controller: 'CoreTotpController'
    });

    $routeProvider.otherwise({
            controller: 'CoreError404',
            templateUrl: '/core:resources/partial/404.html'
        });
});

angular.module('core').run(($location, urlPrefix) => {
    $location._oldPath = $location.path;
    return $location.path = function(path) {
        if (path) {
            path = urlPrefix + path;
        }
        return $location._oldPath(path);
    };
});
