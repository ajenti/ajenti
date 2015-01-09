angular.module('core').directive 'dialog', ($http, $log) ->
    return {
        restrict: 'E'
        scope: {
            dialogClass: '@'
            ngShow: '='
        }
        transclude: true
        template: '''
            <div class="modal" ng:show="ngShow">
                <div class="modal-dialog {{dialogClass}}">
                    <div class="modal-content">
                        <ng-transclude></ng-transclude>
                    </div>
                </div>
            </div>
        '''
        link: ($scope, element, attrs) ->
            element.addClass('block-element')
    }
    