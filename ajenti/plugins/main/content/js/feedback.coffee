class Feedback
    configure: (@enabled, @os, @version, @edition) ->

    emit: (evt, params) ->
        if @enabled
            params ?= {}
            params.os = @os
            params.version = @version
            params.edition = @edition
            mixpanel.track evt, params


window.Feedback = new Feedback()        