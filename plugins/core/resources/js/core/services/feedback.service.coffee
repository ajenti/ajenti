angular.module('core').service 'feedback', ($log, ajentiVersion, ajentiPlatform, ajentiPlatformUnmapped) ->
    @enabled = true # TODO
    @token = 'df4919c7cb869910c1e188dbc2918807'

    mixpanel.init(@token)
    mixpanel.register {
        version: ajentiVersion
        platform: ajentiPlatform
        platformUnmapped: ajentiPlatformUnmapped
    }

    @emit = (evt, params) =>
        if @enabled
            params ?= {}
            params.os = @os
            params.version = @version
            params.edition = @edition
            try
                mixpanel.track evt, params
            catch e
                $log.error e

    return this