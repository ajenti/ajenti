angular.module('core').directive('smartProgress', () =>
    ({
        restrict: 'E',
        scope: {
            animate: '=?',
            value: '=',
            text: '=?',
            max: '=',
            maxText: '=?'
        },
        template: `
            <div>
                <uib-progressbar type="warning" max="100" value="100 * value / max" animate="animate" ng:class="{indeterminate: !max}">
                </uib-progressbar>
            </div>
            <div class="values">
                <span class="pull-left no-wrap">{{text}}</span>
                <span class="pull-right no-wrap">{{maxText}}</span>
            </div>`,
        link($scope, element, attr) {
            $scope.animate = angular.isDefined($scope.animate) ? $scope.animate : true;
        }
    })
);
