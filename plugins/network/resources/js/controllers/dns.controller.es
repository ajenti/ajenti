angular.module('ajenti.network').controller('NetworkDNSController', function($scope, notify, augeas, gettext) {
    augeas.get('resolv').then(config => $scope.config = config);

    $scope.addNameserver = () => {
        $scope.config.insert('nameserver', $scope.newNameserver);
        $scope.newNameserver = '';
    };

    $scope.save = () =>
        augeas.set('resolv', $scope.config).then(() => {
            notify.success(gettext('Saved'))
        }, e => {
            notify.error(gettext('Could not save'), e.message)
        });
});
