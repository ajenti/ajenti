angular.module('ajenti.terminal').controller('TerminalViewController', ($scope, $routeParams, hotkeys, pageTitle) => {
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
    });

    $scope.hideCopyDialogVisible = () => $scope.copyDialogVisible = false;
});
