angular.module('core').service 'messagebox', ($timeout, $q) ->
    @messages = []

    @show = (options) ->
        q = $q.defer()
        options.visible = true
        options.q = q
        @messages.push options
        return {
            then: (f) -> q.promise.then(f)
            catch: (f) -> q.promise.catch(f)
            finally: (f) -> q.promise.finally(f)
            close: () => @close(options)
        }

    @close = (msg) ->
        msg.visible = false
        $timeout () =>
            @messages.remove msg
        , 1000

    return this
