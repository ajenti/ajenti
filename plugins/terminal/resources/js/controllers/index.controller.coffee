angular.module('ajenti.terminal').controller 'TerminalIndexController', ($scope, $location, $q, pageTitle, terminals, urlPrefix) -> 
    pageTitle.set('')

    $scope.refresh = () ->
        q = $q.defer()
        terminals.list().then (list) ->
            $scope.terminals = list
            q.resolve()
        return q.promise

    $scope.create = () ->
        terminals.create().then (id) ->
            $location.path(urlPrefix + "/view/terminal/#{id}")

    $scope.kill = (terminal) ->
        terminals.kill(terminal.id).then () ->
            $scope.refresh()

    $scope.refresh().then () ->
        #if $scope.terminals.length == 0
        #    $scope.create()
