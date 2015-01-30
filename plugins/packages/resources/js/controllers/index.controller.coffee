angular.module('ajenti.packages').controller 'PackagesIndexController', ($scope, $routeParams, $location, notify, pageTitle, urlPrefix, packages, terminals) ->
    pageTitle.set('Packages')

    $scope.managerId = $routeParams.managerId
    $scope.searchQuery = ''
    $scope.results = []
    $scope.selection = []
    $scope.selectionVisible = false

    $scope.$watch 'searchQuery', () ->
        if $scope.searchQuery.length < 3
            return
        $scope.results = null
        packages.list($scope.managerId, $scope.searchQuery).then (data) ->
            $scope.results = data
        .catch (err) ->
            notify.error 'Could not find packages', err.message
            $scope.results = []

    $scope.updateLists = () ->
        packages.updateLists($scope.managerId).then (data) ->
            notify.info 'Package list update started'
        .catch (err) ->
            notify.error 'Package list update failed', err.message

    $scope.mark = (pkg, op) ->
        for sel in $scope.selection
            if sel.package.id == pkg.id
                $scope.selection.remove(sel)
        $scope.selection.push {
            package: pkg
            operation: op
        }

    $scope.markForInstallation = (pkg) ->
        $scope.mark(pkg, 'install')

    $scope.markForUpgrade = (pkg) ->
        $scope.mark(pkg, 'upgrade')

    $scope.markForRemoval = (pkg) ->
        $scope.mark(pkg, 'remove')

    $scope.showSelection = () ->
        $scope.selectionVisible = true

    $scope.hideSelection = () ->
        $scope.selectionVisible = false

    $scope.doApply = () ->
        packages.applySelection($scope.managerId, $scope.selection).then (data) ->
            $scope.selection = []
            cmd = data.terminalCommand
            terminals.create(command: cmd, autoclose: true).then (id) ->
                $location.path("#{urlPrefix}/view/terminal/#{id}")
        .catch () ->
            notify.error 'Could not apply changes'
