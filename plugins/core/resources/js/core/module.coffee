angular.module 'core', [
    'ngAnimate',
    'ngCookies',
    'ngRoute',
    'ngStorage',
    'ngTouch',

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


angular.module('core').run () ->
    FastClick.attach(document.body)


Array.prototype.remove = (args...) ->
    output = []
    for arg in args
        index = @indexOf arg
        output.push @splice(index, 1) if index isnt -1
    output = output[0] if args.length is 1
    output


Array.prototype.contains = (v) ->
    return @indexOf(v) > -1


Array.prototype.toggleItem = (v) ->
    if @contains(v)
        @remove(v)
    else
        @push(v)

