angular.module('core').controller 'CoreIndexController', ($scope, $location, customization, identity, urlPrefix) ->

    $location.path(customization.plugins.core.startupURL or '/view/dashboard')

    identity.promise.then () ->
        if not identity.user
            location.assign("#{urlPrefix}/view/login/normal")
