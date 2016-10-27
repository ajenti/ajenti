angular.module('ajenti.services').controller('ServiceWidgetController', ($scope, services, notify, gettext) => {
    $scope.$on('widget-update', ($event, id, data) => {
        if (id !== $scope.widget.id) {
            return;
        }
        $scope.service = data;
    });

    $scope.runOperation = (o) => {
        let svc = {
            managerId: $scope.widget.config.manager_id,
            id: $scope.widget.config.service_id
        };
        services.runOperation(svc, o).catch(e => notify.error(gettext('Service operation failed'), e.message));
    };
});


angular.module('ajenti.services').controller('ServiceWidgetConfigController', ($scope, services) => {
    $scope.services = [];

    services.getManagers().then((managers) => {
        $scope.managers = managers;

        $scope.managers.forEach((manager) =>
            services.getServices(manager.id).then(services =>
                services.map(service => $scope.services.push(service))
            )
        );
    });
});
