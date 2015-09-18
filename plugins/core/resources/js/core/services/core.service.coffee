angular.module('core').service 'core', ($timeout, $q, $http, $window, messagebox, gettext) ->
    @pageReload = () ->
        $window.location.reload()

    @restart = () ->
        messagebox.show(
            title: gettext('Restart'), 
            text: gettext('Restart the panel?'), 
            positive: gettext('Yes'), 
            negative: gettext('No')
        ).then () =>
            @forceRestart()

    @forceRestart = () ->
        q = $q.defer()
        msg = messagebox.show progress: true, title: gettext('Restarting')
        $http.get('/api/core/restart-master').success () =>
            $timeout () =>
                msg.close()
                q.resolve()
                messagebox.show title: gettext('Restarted'), text: gettext('Please wait')
                $timeout () =>
                    @pageReload()
                    setTimeout () => # sometimes this is not enough
                        @pageReload()
                    , 5000
            , 5000
        .error (err) ->
            msg.close()
            notify.error gettext('Could not restart'), err.message
            q.reject(err)
        return q.promise

    return this