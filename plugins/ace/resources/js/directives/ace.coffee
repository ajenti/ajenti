angular.module('ajenti.ace').directive 'aceEditor', ($timeout, $log) -> 
    return {
        scope: {
            ngModel: '='
            aceOptions: '=?'
        }
        template: '''
            <div ui-ace="options" ng:model="ngModel"></div>
        '''
        link: ($scope, element, attrs) ->
            ace.config.set('basePath', '/resources/ace/resources/vendor/ace-builds/src-min-noconflict')

            element.addClass('block-element')
            $scope.options = $scope.aceOptions
            $scope.options ?= {}
            $scope.options.useWrapMode ?= true
            $scope.options.showGutter ?= true
            $scope.options.theme ?= 'solarized_dark'
            $scope.options.autoScrollEditorIntoView ?= true
            $scope.options.fontSize ?= '12px'
            $scope.options.maxLines ?= Infinity
            $scope.options.scrollPastEnd ?= true

            $scope.options.onLoad = (ace) ->
                $log.debug 'Ace editor loaded'
                $scope.ace = ace
                $scope.ace.setOptions $scope.options
                $scope.ace.resize()

            #element.find('div[ui-ace]').height(900)

            $scope.$on 'ace:reload', ($event, path) ->
                $log.debug 'Guessing mode for ' + path
                $timeout () ->
                    modelist = ace.require('ace/ext/modelist')
                    mode = modelist.getModeForPath(path).mode
                    $scope.ace.getSession().setMode(mode)
    }
