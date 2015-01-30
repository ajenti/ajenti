angular.module('ajenti.terminal').controller 'TerminalViewController', ($scope, $routeParams, hotkeys, pageTitle) ->
    pageTitle.set('Terminal')

    $scope.id = $routeParams.id
    $scope.ready = false
    $scope.copyData = ''
    $scope.copyDialogVisible = false

    $scope.onReady = () ->
        $scope.ready = true

    hotkeys.on $scope, (k, e) ->
        if k == 'C' and e.ctrlKey and e.shiftKey
            $scope.copyDialogVisible = true
            return true
        if k == 'V' and e.ctrlKey and e.shiftKey
            $scope.$broadcast 'terminal:paste'
            return true

    $scope.hideCopyDialogVisible = () ->
        $scope.copyDialogVisible = false
