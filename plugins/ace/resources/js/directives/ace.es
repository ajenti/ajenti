angular.module('ajenti.ace').directive('aceEditor', ($timeout, $log) =>
    ({
        scope: {
            ngModel: '=',
            options: '=?',
            aceOptions: '=?'
        },
        template: '<div ui-ace="options" ng:model="ngModel"></div>',
        link($scope, element, attrs) {
            element.addClass('block-element');
            if ($scope.options) {
                if ($scope.options.height) {
                    element.height($scope.options.height);
                }
                if ($scope.options.fullScreen) {
                    return element.addClass('full-screen');
                }
            }
        },
        controller($scope) {
            if ($scope.options == null)
                $scope.options = {}
            if ($scope.options.useWrapMode == null)
                $scope.options.useWrapMode = true;
            if ($scope.options.showGutter == null)
                $scope.options.showGutter = true;
            if ($scope.aceOptions == null)
                $scope.aceOptions = {};
            if ($scope.aceOptions.theme == null)
                $scope.aceOptions.theme = 'ace/theme/solarized_dark';
            if ($scope.aceOptions.autoScrollEditorIntoView == null)
                $scope.aceOptions.autoScrollEditorIntoView = true;
            if ($scope.aceOptions.fontSize == null)
                $scope.aceOptions.fontSize = '12px';
            if ($scope.aceOptions.maxLines == null)
                $scope.aceOptions.maxLines = Infinity;
            if ($scope.aceOptions.scrollPastEnd == null)
                $scope.aceOptions.scrollPastEnd = true;

            ace.config.set('basePath', '/resources/ace/resources/vendor/ace-builds/src-min-noconflict');

            $scope.options.onLoad = (ace) => {
                $log.debug('Ace editor loaded');
                $scope.ace = ace;
                $scope.ace.$blockScrolling = Infinity;
                $scope.ace.setOptions($scope.aceOptions);
                return $scope.ace.resize();
            };

            return $scope.$on('ace:reload', ($event, path) => {
                $log.debug(`Guessing mode for ${path}`);
                return $timeout(function() {
                    let modelist = ace.require('ace/ext/modelist');
                    let { mode } = modelist.getModeForPath(path);
                    return $scope.ace.getSession().setMode(mode);
                });
            });
        }
    })
);
