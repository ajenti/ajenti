angular.module('ajenti.session_list').controller 'SessionListIndexController', ($scope, $http, $interval, $timeout, notify, pageTitle, messagebox, gettext, config) ->
    pageTitle.set(gettext('List all sessions'))

    $scope.getList = () ->
        $http.get('/api/session_list/list').then (resp) ->
            $scope.sessions = resp.data
            for session in $scope.sessions
                session.date = new Date(session.timestamp)
            $scope.number = Object.keys($scope.sessions).length
            $scope.session_max_time = config.data.session_max_time

    $scope.getList()

    # Refresh list every 15s
    $scope.refresh = $interval($scope.getList, 15000, 0)

    $scope.$on('$destroy', () -> $interval.cancel($scope.refresh))
