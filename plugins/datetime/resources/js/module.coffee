angular.module 'ajenti.datetime', [
    'core',
]

angular.module('ajenti.datetime').run (customization) ->
    customization.plugins.datetime = {}
