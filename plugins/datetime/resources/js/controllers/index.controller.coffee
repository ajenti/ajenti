angular.module('ajenti.datetime').controller 'DateTimeIndexController', ($scope, $interval, $timeout, notify, pageTitle, datetime, gettext) ->
    pageTitle.set(gettext('Date & Time'))

    datetime.listTimezones().then (data) ->
        $scope.timezones = data

    $scope.refresh = () ->
        datetime.getTimezone().then (data) ->
            $scope.timezone = data.tz
            $scope.offset = data.offset

            datetime.getTime().then (time) ->
                $scope._.time = new Date(time * 1000)

                #int = $interval () ->
                #    $scope._.time = new Date($scope._.time.getTime() + 1000)
                #, 1000

                #$scope.$on '$destroy', () ->
                #    $interval.cancel(int)

    $scope.refresh()

    $scope._ = {}

    $scope.setTimezone = () ->
        datetime.setTimezone($scope.timezone).then () ->
            $timeout () ->
                $scope.refresh()
                notify.success gettext('Timezone set')
            , 1000
        .catch (e) ->
            notify.error gettext('Failed'), e.message

    $scope.setTime = () ->
        datetime.setTime($scope._.time.getTime() / 1000).then () ->
            notify.success gettext('Time set')
        .catch (e) ->
            notify.error gettext('Failed'), e.message

    $scope.syncTime = () ->
        notify.info gettext('Synchronizing...')
        datetime.syncTime().then (time) ->
            $scope._.time = new Date(time * 1000)
            notify.success gettext('Time synchronized')
        .catch (e) ->
            notify.error gettext('Failed'), e.message
