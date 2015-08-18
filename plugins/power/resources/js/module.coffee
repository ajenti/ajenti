angular.module 'ajenti.power', [
    'core',
]

angular.module('ajenti.power').run (customization) ->
    customization.plugins.power = {}
