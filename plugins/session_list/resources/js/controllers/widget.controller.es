angular.module('ajenti.session_list').controller('SessionWidgetController', ($scope, $http) =>
    $scope.$on('widget-update', function($event, id, data) {
        if (id !== $scope.widget.id) {
            return;
        }

        if (data) {
            $http.get('/api/session_list/sessions').then((resp) => {
                $scope.sessions = resp.data;
                for (let session in $scope.sessions)
                    session.date = new Date(session.timestamp);
                $scope.number = Object.keys($scope.sessions).length;
           });
        }
    })
);

