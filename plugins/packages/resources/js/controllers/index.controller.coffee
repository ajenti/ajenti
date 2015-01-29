angular.module('ajenti.packages').controller 'PackagesIndexController', ($scope, $routeParams, notify, pageTitle, packages) ->
    pageTitle.set('Packages')

    $scope.managerId = $routeParams.managerId
    $scope.searchQuery = ''
    $scope.results = []

    $scope.$watch 'searchQuery', () ->
        if $scope.searchQuery.length < 3
            return
        $scope.results = null
        packages.list($scope.managerId, $scope.searchQuery).then (data) ->
            $scope.results = data
        .error (err) ->
            notify.error 'Could not find packages', err.message
            $scope.results = []
