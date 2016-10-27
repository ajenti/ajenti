angular.module('ajenti.services').controller('ServicesIndexController', function($scope, $routeParams, notify, pageTitle, services, gettext) {
    pageTitle.set(gettext('Services'));

    $scope.services = [];

    services.getManagers().then((managers) => {
        $scope.managers = managers;

        for (let manager of $scope.managers) {
            if ($routeParams.managerId && manager.id !== $routeParams.managerId) {
                continue;
            }
            services.getServices(manager.id).then(services => {
                for (let service of services)
                    $scope.services.push(service);
            });
        }
    });

    $scope.runOperation = (service, operation) =>
        services.runOperation(service, operation).then(() =>
            services.getService(service.managerId, service.id).then(function(data) {
                angular.copy(data, service);
                return notify.success(gettext('Done'));
            })
        )
        .catch(err => notify.error(gettext('Service operation failed'), err.message));
});
