angular.module('core').service 'customization', ($rootScope) ->
    $rootScope.customization = this
    @plugins = {core: {
        extraProfileMenuItems: []
    }}
    return @this
