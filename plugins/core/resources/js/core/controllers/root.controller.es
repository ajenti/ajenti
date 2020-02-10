angular.module('core').controller('CoreRootController', function($scope, $rootScope, $location, $localStorage, $log, $timeout, $q, $interval, $http, $window, identity, customization, urlPrefix, ajentiPlugins, ajentiVersion, ajentiPlatform, ajentiPlatformUnmapped, favicon, feedback, locale, config) {
    $rootScope.identity = identity;
    $rootScope.$location = $location;
    $rootScope.location = location;
    $rootScope.urlPrefix = urlPrefix;
    $rootScope.feedback = feedback;
    $rootScope.ajentiVersion = ajentiVersion;
    $rootScope.ajentiPlugins = ajentiPlugins;
    $rootScope.customization = customization;

    // todo figure this out, used in settings template
    $rootScope.keys = function(x) { if (x) { return Object.keys(x); } else { return []; } };

    console.group('Welcome');
    console.info('Ajenti', ajentiVersion);
    console.log('Running on', ajentiPlatform, '/', ajentiPlatformUnmapped);
    if (urlPrefix) {
        console.log('URL prefix', urlPrefix);
    }
    console.log('Plugins', ajentiPlugins);
    console.groupEnd();

    $scope.navigationPresent = $location.path().indexOf('/view/login') === -1;

    feedback.init();

    // ---

    $scope.showSidebar = angular.isDefined($localStorage.showSidebar) ? $localStorage.showSidebar : true
    $rootScope.toggleNavigation = (state) => {
        if (angular.isDefined(state)) {
            $scope.showSidebar = state;
        } else {
            $scope.showSidebar = !$scope.showSidebar;
        }
        $localStorage.showSidebar = $scope.showSidebar;
        $scope.$broadcast('navigation:toggle');
    };

    // ---
    $scope.showOverlaySidebar = false
    $rootScope.toggleOverlayNavigation = (state) => {
        if (angular.isDefined(state)) {
            $scope.showOverlaySidebar = state
        } else {
            $scope.showOverlaySidebar = !$scope.showOverlaySidebar
        }
        $scope.$broadcast('navigation:toggle')
    }

    $scope.$on('$routeChangeStart', function() {
        $scope.updateResttime();
    })

    $scope.$on('$routeChangeSuccess', function() {
        $scope.toggleOverlayNavigation(false)
        feedback.emit('navigation', {url: $location.path()});
    })

    // ---

    $scope.isWidescreen = angular.isDefined($localStorage.isWidescreen) ? $localStorage.isWidescreen : false

    $scope.toggleWidescreen = function(state) {
        if (angular.isDefined(state)) {
            $scope.isWidescreen = state;
        } else {
            $scope.isWidescreen = !$scope.isWidescreen;
        }
        $localStorage.isWidescreen = $scope.isWidescreen;
        $scope.$broadcast('widescreen:toggle');
    };

    // ---

    identity.init();
    identity.promise.then(function() {
        $log.info('Identity', identity.user);
        return $rootScope.appReady = true;
    });

    favicon.init();

    setTimeout(() =>
        $(window).resize(() => {
            $scope.$apply(() => $rootScope.$broadcast('window:resize'))
        })
    );

    $scope.updateResttime = function() {
        if ($location.path() != '/view/login/normal') {
            $http.get('/api/core/session-time').then((resp) => {
                $rootScope.resttime = resp.data;
                $rootScope.counter = $scope.convertTime($rootScope.resttime);
                if ($rootScope.resttime > 0 && !angular.isDefined($scope.timeDown)) {
                    $scope.timeDown = $interval($scope.countDown, 1000, 0);
                }
            });
        };
    };

    $scope.updateResttime();

    $scope.countDown = function() {
        if ($rootScope.resttime <= 0) {
            $interval.cancel($scope.timeDown);
            $scope.timeDown = null;
            $window.location.href = '/view/login/normal';
        }
        else {
            $rootScope.resttime -= 1;
            $rootScope.counter = $scope.convertTime($rootScope.resttime);
        }
    };

    $scope.convertTime = function(seconds) {
        hours = ('00' + Math.floor(seconds/3600)).slice(-2);
        rest = seconds % 3600;
        minutes = ('00' + Math.floor(rest/60)).slice(-2);
        seconds = ('00' + rest % 60).slice(-2);
        return [hours, minutes, seconds]
    };

});
