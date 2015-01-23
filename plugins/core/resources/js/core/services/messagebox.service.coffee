angular.module('core').service 'messagebox', ($timeout, $q) ->
    @messages = []

    @show = (options) ->
        q = $q.defer()
        options.visible = true
        options.q = q
        @messages.push options
        return q.promise

    @close = (msg) ->
        msg.visible = false
        $timeout () =>
            @messages.remove msg
        , 1000

    return this
