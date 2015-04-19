angular.module('ajenti.services').controller 'ServicesIndexController', ($scope, $routeParams, notify, pageTitle, services) ->
    pageTitle.set('Services')

    $scope.services = []

    services.getManagers().then (managers) ->
        $scope.managers = managers

        for manager in $scope.managers
            if $routeParams.managerId and manager.id != $routeParams.managerId
                continue
            services.getServices(manager.id).then (services) ->
                for service in services
                    $scope.services.push service

    $scope.runOperation = (service, operation) ->
        services.runOperation(service, operation).then () ->
            services.getService(service.managerId, service.id).then (data) ->
                angular.copy(data, service)
                notify.success 'Done'
        .catch (err) ->
            notify.error 'Service operation failed', err.message
