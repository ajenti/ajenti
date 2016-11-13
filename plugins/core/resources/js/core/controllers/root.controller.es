angular.module('core').controller('CoreRootController', function($scope, $rootScope, $location, $localStorage, $log, $timeout, $q, identity, customization, urlPrefix, ajentiPlugins, ajentiVersion, ajentiPlatform, ajentiPlatformUnmapped, favicon, feedback, locale, config) {
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

    $scope.$on('$routeChangeSuccess', function() {
        feedback.emit('navigation', {url: $location.path()});
    });

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
});
