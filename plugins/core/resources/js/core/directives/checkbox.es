angular.module('core').directive('checkbox', () =>
    ({
        restrict: 'EA',
        scope: {
            text: '@',
            toggle: '='
        },
        require: 'ngModel',
        template: "<i class=\"fa fa-square-o off\"></i><i class=\"fa fa-check-square on\"></i> {{text}}",
        link($scope, element, attr, ngModelController) {
            let classToToggle = 'active';

            ngModelController.$render = function() {
                if (ngModelController.$viewValue) {
                    element.addClass(classToToggle);
                } else {
                    element.removeClass(classToToggle);
                }
            };

            element.bind('click', () =>
                $scope.$apply(() => {
                    ngModelController.$setViewValue(!ngModelController.$viewValue);
                    ngModelController.$render();
                })
            );

            if ($scope.toggle) {
                ngModelController.$formatters.push(v => v === $scope.toggle[1]);
                ngModelController.$parsers.push(v => v ? $scope.toggle[1] : $scope.toggle[0]);
            }
        }
    })
);
