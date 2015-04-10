angular.module('core').controller 'CoreRootController', ($scope, $rootScope, $location, $cookieStore, $q, identity, urlPrefix, ajentiPlugins, ajentiVersion, favicon, feedback) ->
    $rootScope.identity = identity
    $rootScope.$location = $location
    $rootScope.location = location
    $rootScope.urlPrefix = urlPrefix
    $rootScope.feedback = feedback
    $rootScope.ajentiVersion = ajentiVersion
    $rootScope.ajentiPlugins = ajentiPlugins

    # todo figure this out, used in settings template
    $rootScope.keys = (x) -> if x then Object.keys(x) else []

    console.group('Welcome')
    console.log('Ajenti', ajentiVersion)
    if urlPrefix
        console.log('URL prefix', urlPrefix)
    console.log('Plugins', ajentiPlugins)
    console.groupEnd()

    $scope.navigationPresent = $location.path().indexOf('/view/login') != 0

    feedback.init()

    # ---

    $scope.showSidebar = $cookieStore.get('showSidebar') ? true
    $rootScope.toggleNavigation = (state) ->
        if angular.isDefined state
            $scope.showSidebar = state
        else
            $scope.showSidebar = !$scope.showSidebar
        $cookieStore.put('showSidebar', $scope.showSidebar)
        $scope.$broadcast 'navigation:toggle'

    # ---

    $scope.showOverlaySidebar = false
    $rootScope.toggleOverlayNavigation = (state) ->
        if angular.isDefined state
            $scope.showOverlaySidebar = state
        else
            $scope.showOverlaySidebar = !$scope.showOverlaySidebar
        $scope.$broadcast 'navigation:toggle'

    $scope.$on '$routeChangeSuccess', () ->
        $scope.toggleOverlayNavigation(false)
        feedback.emit 'navigation', url: $location.path()

    # ---

    $scope.isWidescreen = $cookieStore.get('isWidescreen') ? false
    $scope.toggleWidescreen = (state) ->
        if angular.isDefined state
            $scope.isWidescreen = state
        else
            $scope.isWidescreen = !$scope.isWidescreen
        $cookieStore.put('isWidescreen', $scope.isWidescreen)
        $scope.$broadcast 'widescreen:toggle'

    # ---

    $rootScope.appReady = true
    identity.init()
    identity.promise.then () ->
        console.log 'Ready!'
    .catch () ->
        console.error 'Failed'

    favicon.init()

    $rootScope.theme = 'deeporange'

    setTimeout () ->
        $(window).resize () ->
            $scope.$apply () ->
                $rootScope.$broadcast 'window:resize'
