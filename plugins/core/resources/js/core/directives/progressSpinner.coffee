angular.module('core').directive 'progressSpinner', () ->
    return {
        restrict: 'E'
        template: '''
            <div>
                <div class="one"></div>
                <div class="two"></div>
            </div>
        '''
        link: ($scope, element, attrs) ->
    }
