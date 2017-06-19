angular.module('ajenti.power').controller('PowerIndexController', ($scope, $interval, notify, pageTitle, power, messagebox, gettext) => {
    pageTitle.set(gettext('Power management'));

    power.getUptime().then(uptime => {
        $scope.uptime = uptime;

        let int = $interval(() =>
            $scope.uptime += 1
        , 1000);

        $scope.$on('$destroy', () => $interval.cancel(int));
    });

    power.getBatteries().then(batteries => $scope.batteries = batteries);

    power.getAdapters().then(adapters => $scope.adapters = adapters);

    $scope.poweroff = () =>
        messagebox.show({
            title: gettext('Warning'),
            text: gettext('Are you sure you want to shutdown the system now?'),
            positive: gettext('Shutdown'),
            negative: gettext('Cancel')
        }).then(() =>
            power.poweroff().then(() => messagebox.show({progress: true, text: 'System is shutting down'}))
        );

    $scope.reboot = () =>
        messagebox.show({
            title: gettext('Warning'),
            text: gettext('Are you sure you want to reboot the system now?'),
            positive: gettext('Reboot'),
            negative: gettext('Cancel')
        }).then(() =>
            power.reboot().then(() => messagebox.show({
                progress: true,
                text: gettext('System is rebooting. We will try to reconnect with it.')
            }))
        );

    $scope.suspend = () =>
        messagebox.show({
            title: gettext('Warning'),
            text: gettext('Are you sure you want to suspend the system now?'),
            positive: gettext('Suspend'),
            negative: gettext('Cancel')
        }).then(() =>
            power.suspend().then(() => messagebox.show({progress: true, text: gettext('System is suspending')}))
        );

    $scope.hibernate = () =>
        messagebox.show({
            title: gettext('Warning'),
            text: gettext('Are you sure you want to hibernate the system now?'),
            positive: gettext('Hibernate'),
            negative: gettext('Cancel')
        }).then(() =>
            power.hibernate().then(() => messagebox.show({progress: true, text: gettext('System is hibernating')}))
        );
});
