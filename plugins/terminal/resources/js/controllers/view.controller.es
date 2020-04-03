angular.module('ajenti.terminal').controller('TerminalViewController', ($scope, $routeParams, $interval, terminals, hotkeys, pageTitle) => {
    pageTitle.set('Terminal');

    $scope.id = $routeParams.id;
    $scope.ready = false;
    $scope.copyData = '';
    $scope.copyDialogVisible = false;

    $scope.onReady = () => $scope.ready = true;

    hotkeys.on($scope, function(k, e) {
        if (k === 'C' && e.ctrlKey && e.shiftKey) {
            $scope.copyDialogVisible = true;
            return true;
        }
        if (k === 'V' && e.ctrlKey && e.shiftKey) {
            $scope.$broadcast('terminal:paste');
            return true;
        }
        if (k === 'D' && e.ctrlKey) {
            terminals.kill($scope.id);
            return true;
        }
    });

    $scope.check = () => {
        terminals.is_dead($scope.id);
    }

    $scope.redirect_if_dead = $interval($scope.check, 4000, 0);

    $scope.$on('$destroy', function() {
        $interval.cancel($scope.redirect_if_dead);
    });

    $scope.hideCopyDialogVisible = () => $scope.copyDialogVisible = false;
});
