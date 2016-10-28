angular.module('core').service('core', function($timeout, $q, $http, $window, messagebox, gettext) {
    this.pageReload = () => $window.location.reload();

    this.restart = () =>
        messagebox.show({
            title: gettext('Restart'),
            text: gettext('Restart the panel?'),
            positive: gettext('Yes'),
            negative: gettext('No')
        }).then(() => {
            this.forceRestart();
        });

    this.forceRestart = () => {
        let msg = messagebox.show({progress: true, title: gettext('Restarting')});
        return $http.get('/api/core/restart-master').then(() => {
            return $timeout(() => {
                msg.close();
                messagebox.show({title: gettext('Restarted'), text: gettext('Please wait')});
                $timeout(() => {
                    this.pageReload();
                    return setTimeout(() => { // sometimes this is not enough
                        return this.pageReload();
                    }, 5000);
                });
            }, 5000);
        }).catch((err) => {
            msg.close();
            notify.error(gettext('Could not restart'), err.message);
            return $q.reject(err);
        });
    };

    return this;
});
