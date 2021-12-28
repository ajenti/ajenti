angular.module('ajenti.services').controller('ServicesIndexController', function($scope, $routeParams, $uibModal, notify, pageTitle, services, gettext) {
    pageTitle.set(gettext('Services'));

    $scope.services = [];
    $scope.titles = {
        'stop': gettext("Stop service"),
        'start': gettext("Start service"),
        'restart': gettext("Restart service"),
        'kill': gettext("Kill service"),
        'enable': gettext("Enable service"),
        'disable': gettext("Disable service"),
    }

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

    $scope.showStatus = (service) => {
        services.getStatus(service.managerId, service.id).then(function(data) {
            $scope.status = data;
            $uibModal.open({
                templateUrl: '/services:resources/partial/systemd_status.modal.html',
                controller: 'SystemdStatusModalController',
                size: 'lg',
                resolve: {
                    service: () => $scope.service,
                    status: () => $scope.status
                }
            });
        })
    }

    $scope.closeStatus = () => {
        $scope.showDialog = false;
        $scope.selectedService = "";
    }

    $scope.runOperation = (service, operation) =>
        services.runOperation(service, operation).then(() =>
            services.getService(service.managerId, service.id).then(function(data) {
                angular.copy(data, service);
                return notify.success(gettext('Done'));
            })
        )
        .catch(err => notify.error(gettext('Service operation failed'), err.message));
});

angular.module('ajenti.services').controller('SystemdStatusModalController', function($scope, $uibModalInstance, gettext, notify, service, status) {

    $scope.service = service;
    $scope.status = status;

    $scope.close = () =>
        $uibModalInstance.close();
});