angular.module 'app', window.__ngModules

angular.module('app').config ($locationProvider) ->
    $locationProvider.html5Mode(enabled: true, requireBase: false)
