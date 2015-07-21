angular.module('core').directive 'datepickerPopup', () ->
    return {
        restrict: 'EAC'
        require: 'ngModel'
        link: (scope, element, attr, controller) ->
            controller.$formatters.shift()
    }