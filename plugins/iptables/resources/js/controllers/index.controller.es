angular.module('ajenti.iptables').controller('IptablesIndexController', function($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Iptables'));

    $http.get('/api/iptables/which').then(() => {
            $scope.load();
            $scope.installed = true;
        }
        , (err) => {
            $scope.ready = true;
            $scope.installed = false;
        }
    );

    $scope.load = () => {
        $http.get('/api/iptables').then((resp) => {
            $scope.chains = resp.data;
            $scope.chains_list = Object.keys(resp.data);
            if ($scope.chains_list.length > 0) {
                $scope.chains.active_chain = $scope.chains_list[0];
                $scope.rules = $scope.chains[$scope.chains.active_chain];
            } else {
                $scope.chains.active_chain = '';
            }
        });
    }

    $scope.update_rules = () => {
        console.log($scope.chains.active_chain);
        $scope.rules = $scope.chains[$scope.chains.active_chain];
    }
});

