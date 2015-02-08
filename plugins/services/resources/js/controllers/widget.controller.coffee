angular.module('ajenti.services').controller 'ServiceWidgetController', ($scope, services) ->
    $scope.$on 'widget-update', ($event, id, data) ->
        if id != $scope.widget.id
            return
        $scope.service = data

    $scope.runOperation = (o) ->
        svc =
            managerId: $scope.widget.config.manager_id
            id: $scope.widget.config.service_id
        services.runOperation(svc, o)


angular.module('ajenti.services').controller 'ServiceWidgetConfigController', ($scope, services) ->
    $scope.services = []

    services.getManagers().then (managers) ->
        $scope.managers = managers

        for manager in $scope.managers
            services.getServices(manager.id).then (services) ->
                for service in services
                    $scope.services.push service
