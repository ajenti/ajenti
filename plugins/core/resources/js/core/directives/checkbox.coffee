angular.module('core').directive 'checkbox', () ->
    return {
        restrict: 'A'
        scope: {
            text: '@'
            ngModel: '=?'
            ngChecked: '=?'
        }
        template: """
            <i class="fa fa-square-o off"></i><i class="fa fa-check-square on"></i> {{text}}
        """
        link: ($scope, element, attr) ->
            classToToggle = 'active'
            element.bind 'click', () ->
                $scope.$apply (scope) ->
                    if angular.isDefined($scope.ngChecked)
                        return
                    $scope.ngModel = !$scope.ngModel
                    
            $scope.$watch 'ngModel', (newValue) ->
                if not attr.ngModel
                    return
                if newValue then element.addClass(classToToggle) else element.removeClass(classToToggle)

            $scope.$watch 'ngChecked', (newValue) ->
                if not attr.ngChecked
                    return
                if newValue then element.addClass(classToToggle) else element.removeClass(classToToggle)
    }
