angular.module 'core', [
    'ngAnimate',
    'ngCookies',
    'ngRoute',
    'ngStorage',

    'angular-loading-bar',
    'btford.socket-io',
    'persona',
    'toaster',
    'ui.bootstrap',
]


angular.module('core').config ($httpProvider, $animateProvider, $compileProvider) ->
    $httpProvider.interceptors.push 'urlPrefixInterceptor'
    $httpProvider.interceptors.push 'unauthenticatedInterceptor'
    $animateProvider.classNameFilter /animate.+/
    $compileProvider.aHrefSanitizationWhitelist /^\s*(https?|ftp|mailto|data|file):/
