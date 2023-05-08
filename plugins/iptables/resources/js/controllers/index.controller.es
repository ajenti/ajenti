angular.module('ajenti.iptables').controller('IptablesIndexController', function($scope, $http, pageTitle, gettext, notify, messagebox) {
    pageTitle.set(gettext('Iptables'));

    $scope.paging = {
        'page': 1
    }

    $http.get('/api/iptables/which').then(() => {
            $scope.load();
            $scope.installed = true;
        }
        , (err) => {
            $scope.ready = true;
            $scope.installed = false;
        }
    );

    $scope.load = (chain) => {
        $http.get('/api/iptables').then((resp) => {
            $scope.chains = resp.data;
            $scope.chains_list = Object.keys(resp.data);
            if ($scope.chains_list.length > 0) {
                if ($scope.chains_list.indexOf(chain) > 0) {
                    $scope.chains.active_chain = chain;
                } else {
                    $scope.chains.active_chain = $scope.chains_list[0];
                }
                $scope.rules = $scope.chains[$scope.chains.active_chain];
            } else {
                $scope.chains.active_chain = '';
            }
        });
    }

    $scope.update_rules = () => {
        $scope.rules = $scope.chains[$scope.chains.active_chain];
    }

    $scope.delete = (rule) => {
        messagebox.show({
            text: gettext(`Really delete the rule ${rule.rule_line}?`),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(() => {
            $http.delete(`/api/iptables/${$scope.chains.active_chain}/${rule.number}`).then((resp) => {
                type = resp.data.type;
                msg = resp.data.msg;
                chain = $scope.chains.active_chain;
                if (type == 'success') {
                    notify.success(msg);
                    $scope.load(chain);
                } else {
                    notify.error(msg);
                }
            });
        });
    }
});

