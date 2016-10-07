angular.module('core', [
    'ngAnimate',
    'ngCookies',
    'ngRoute',
    'ngStorage',
    'ngTouch',

    'angular-loading-bar',
    'btford.socket-io',
    'toaster',
    'ui.bootstrap',
    'angular-sortable-view',
    'base64',
    'gettext',
]);


angular.module('core').config(($httpProvider, $animateProvider, $compileProvider) => {
    $httpProvider.interceptors.push('urlPrefixInterceptor');
    $httpProvider.interceptors.push('unauthenticatedInterceptor');
    $animateProvider.classNameFilter(/animate.+/);
    $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|data|file):/);
});


angular.module('core').run(() => FastClick.attach(document.body));


angular.module('core').factory('$exceptionHandler', ($injector, $log, gettext) =>
    function(exception, cause) {
        if (!exception.toString().startsWith('Possibly unhandled rejection')) {
            $injector.get('notify').warning(gettext('Unhanded error occured'), gettext('Please see browser console'));
        }

        console.group('Unhandled exception occured');
        console.warn('Consider sending this error to https://github.com/ajenti/ajenti/issues/new');
        $log.error.apply($log, arguments);
        return console.groupEnd();
    }
);
