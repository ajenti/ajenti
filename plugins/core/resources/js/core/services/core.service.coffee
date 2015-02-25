angular.module('core').service 'core', ($timeout, $q, $http, identity, messagebox) ->
    @restart = () ->
        messagebox.show(title: 'Restart', text: 'Restart the panel?', positive: 'Yes', negative: 'No').then () =>
            @forceRestart()

    @forceRestart = () ->
        q = $q.defer()
        msg = messagebox.show progress: true, title: 'Restarting'
        $http.get('/api/core/restart-master').success () ->
            $timeout () ->
                msg.close()
                q.resolve()
                messagebox.show title: 'Restarted', text: 'Please wait'
                setTimeout () ->
                    location.reload()
                    setTimeout () -> # sometimes this is not enough
                        location.reload()
                    , 5000
            , 5000
        .error (err) ->
            msg.close()
            notify.error 'Could not restart', err.message
            q.reject(err)
        return q.promise

    return this