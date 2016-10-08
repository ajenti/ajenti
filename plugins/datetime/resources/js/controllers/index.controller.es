angular.module('ajenti.datetime').controller('DateTimeIndexController', function($scope, $interval, $timeout, notify, pageTitle, datetime, gettext) {
    pageTitle.set(gettext('Date & Time'));

    datetime.listTimezones().then(data => $scope.timezones = data);

    $scope.refresh = () =>
        datetime.getTimezone().then((data) => {
            $scope.timezone = data.tz;
            $scope.offset = data.offset;

            $scope._.time = undefined;
            datetime.getTime().then(time => $scope._.time = new Date((time + $scope.offset) * 1000));
        })
    ;

    $scope.refresh();

    $scope._ = {};

    $scope.setTimezone = () =>
        datetime.setTimezone($scope.timezone).then(() =>
            $timeout(() => {
                $scope.refresh();
                notify.success(gettext('Timezone set'));
            }, 1000)
        ).catch(e => notify.error(gettext('Failed'), e.message))
    ;

    $scope.setTime = () =>
        datetime.setTime(($scope._.time.getTime() / 1000) - $scope.offset).then(() => notify.success(gettext('Time set')), e => notify.error(gettext('Failed'), e.message));

    $scope.syncTime = function() {
        notify.info(gettext('Synchronizing...'));
        return datetime.syncTime().then((time) => {
            $scope._.time = new Date(time * 1000);
            notify.success(gettext('Time synchronized'));
        }, (e) => notify.error(gettext('Failed'), e.message));
    };
});
