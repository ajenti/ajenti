angular.module('ajenti.services').controller 'ServicesIndexController', ($scope, $routeParams, notify, pageTitle, services, gettext) ->
    pageTitle.set(gettext('Services'))

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
                notify.success gettext('Done')
        .catch (err) ->
            notify.error gettext('Service operation failed'), err.message
