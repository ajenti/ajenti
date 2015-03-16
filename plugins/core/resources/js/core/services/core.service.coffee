angular.module('core').service 'core', ($timeout, $q, $http, $window, messagebox) ->
    @pageReload = () ->
        $window.location.reload()

    @restart = () ->
        messagebox.show(title: 'Restart', text: 'Restart the panel?', positive: 'Yes', negative: 'No').then () =>
            @forceRestart()

    @forceRestart = () ->
        q = $q.defer()
        msg = messagebox.show progress: true, title: 'Restarting'
        $http.get('/api/core/restart-master').success () =>
            $timeout () =>
                msg.close()
                q.resolve()
                messagebox.show title: 'Restarted', text: 'Please wait'
                $timeout () =>
                    @pageReload()
                    setTimeout () => # sometimes this is not enough
                        @pageReload()
                    , 5000
            , 5000
        .error (err) ->
            msg.close()
            notify.error 'Could not restart', err.message
            q.reject(err)
        return q.promise

    return this