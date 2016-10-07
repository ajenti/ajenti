angular.module('core').directive('datepickerPopup', () =>
    ({
        restrict: 'EAC',
        require: 'ngModel',
        link(scope, element, attr, controller) {
            controller.$formatters.shift();
        }
    })
);
