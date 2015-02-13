angular.module('core').controller 'CoreNavboxController', ($scope, $http, $location, hotkeys) ->
    $scope.results = null

    hotkeys.on $scope, (key, event) ->
        if key == 'P' and event.ctrlKey
            $scope.visible = true
            return true
        return false
    , 'keydown'

    $scope.cancel = () ->
        $scope.visible = false
        $scope.query = null

    $scope.onSearchboxKeyDown = ($event) ->
        if $scope.results
            if $event.keyCode == hotkeys.ENTER
                $scope.open($scope.results[0])
            for i in [0...Math.min($scope.results.length, 10)]
                if $event.keyCode == i.toString().charCodeAt(0) and $event.shiftKey
                    $scope.open($scope.results[i])
                    $event.preventDefault()

    $scope.onSearchboxKeyUp = ($event) ->
        if $event.keyCode == hotkeys.ESC
            $scope.cancel()

    $scope.$watch 'query', () ->
        if not $scope.query
            return
        $http.get("/api/core/navbox/#{$scope.query}").success (results) ->
            $scope.results = results

    $scope.open = (result) ->
        $location.path(result.url)
        $scope.cancel()
