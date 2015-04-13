angular.module('ajenti.datetime').controller 'DateTimeIndexController', ($scope, $interval, notify, pageTitle, datetime) ->
    pageTitle.set('Date & Time')

    datetime.listTimezones().then (data) ->
        $scope.timezones = data

    datetime.getTimezone().then (data) ->
        $scope.timezone = data

    $scope._ = {}

    datetime.getTime().then (time) ->
        $scope._.time = new Date(time * 1000)

        int = $interval () ->
            $scope._.time = new Date($scope._.time.getTime() + 1000)
        , 1000

        $scope.$on '$destroy', () ->
            $interval.cancel(int)

    $scope.setTime = () ->
        datetime.setTimezone($scope.timezone).then () ->
            datetime.setTime($scope._.time.getTime() / 1000).then () ->
                notify.success 'Time set'
            .catch (e) ->
                notify.error 'Failed', e.message
        .catch (e) ->
            notify.error 'Failed', e.message
    
    $scope.syncTime = () ->
        notify.info 'Synchronizing...'
        datetime.syncTime().then (time) ->
            $scope._.time = new Date(time * 1000)
            notify.success 'Time synchronized'
        .catch (e) ->
            notify.error 'Failed', e.message
