class Feedback
    configure: (@enabled, @os, @version, @edition) ->
        mixpanel.init(@token)

    emit: (evt, params) ->
        if @enabled
            params ?= {}
            params.os = @os
            params.version = @version
            params.edition = @edition
            try
                mixpanel.track evt, params
            catch e
                ;


window.Feedback = new Feedback()        
window.Feedback.token = "b5e6ddf58b2d02245a7a19005d1cec48"