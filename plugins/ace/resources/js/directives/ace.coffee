angular.module('ajenti.ace').directive 'aceEditor', ($timeout, $log) -> 
    return {
        scope: {
            ngModel: '='
            options: '=?'
            aceOptions: '=?'
        }
        template: '''
            <div ui-ace="options" ng:model="ngModel"></div>
        '''
        link: ($scope, element, attrs) ->
            element.addClass('block-element')
            if $scope.options 
                if $scope.options.height
                    element.height($scope.options.height)
                if $scope.options.fullScreen
                    element.addClass('full-screen')

        controller: ($scope) ->
            $scope.options ?= {}
            $scope.options.useWrapMode ?= true
            $scope.options.showGutter ?= true
            $scope.aceOptions ?= {}
            $scope.aceOptions.theme ?= 'ace/theme/solarized_dark'
            $scope.aceOptions.autoScrollEditorIntoView ?= true
            $scope.aceOptions.fontSize ?= '12px'
            $scope.aceOptions.maxLines ?= Infinity
            $scope.aceOptions.scrollPastEnd ?= true
            ace.config.set('basePath', '/resources/ace/resources/vendor/ace-builds/src-min-noconflict')

            $scope.options.onLoad = (ace) ->
                $log.debug 'Ace editor loaded'
                $scope.ace = ace
                $scope.ace.$blockScrolling = Infinity
                $scope.ace.setOptions $scope.aceOptions
                $scope.ace.resize()

            $scope.$on 'ace:reload', ($event, path) ->
                $log.debug 'Guessing mode for ' + path
                $timeout () ->
                    modelist = ace.require('ace/ext/modelist')
                    mode = modelist.getModeForPath(path).mode
                    $scope.ace.getSession().setMode(mode)
    }
