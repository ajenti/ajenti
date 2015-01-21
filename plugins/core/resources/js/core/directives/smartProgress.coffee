angular.module('core').directive 'smartProgress', () ->
    return {
        restrict: 'E'
        scope: {
            animate: '=?'
            value: '='
            text: '=?'
            max: '='
            maxText: '=?'
        }
        template: """
        <div>
            <progressbar type="warning" max="100" value="100 * value / max" animate="animate" ng:class="{indeterminate: !max}">
            </progressbar>
        </div>
        <div class="values">
            <span class="pull-left no-wrap">{{text}}</span>
            <span class="pull-right no-wrap">{{maxText}}</span>
        </div>
        """
        link: ($scope, element, attr) ->
            $scope.animate ?= true
    }

