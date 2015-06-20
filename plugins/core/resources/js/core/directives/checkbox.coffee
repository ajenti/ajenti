angular.module('core').directive 'checkbox', () ->
    return {
        restrict: 'EA'
        scope: {
            text: '@'
            toggle: '='
        }
        require: 'ngModel',
        template: """
            <i class="fa fa-square-o off"></i><i class="fa fa-check-square on"></i> {{text}}
        """
        link: ($scope, element, attr, ngModelController) ->
            classToToggle = 'active'

            ngModelController.$render = () ->
                if ngModelController.$viewValue
                    element.addClass(classToToggle)
                else
                    element.removeClass(classToToggle)

            element.bind 'click', () ->
                $scope.$apply (scope) ->
                    ngModelController.$setViewValue(!ngModelController.$viewValue)
                    ngModelController.$render()

            if $scope.toggle
                ngModelController.$formatters.push (v) ->
                    return v == $scope.toggle[1]
                ngModelController.$parsers.push (v) ->
                    return if v then $scope.toggle[1] else $scope.toggle[0]
    }
