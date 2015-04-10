angular.module('core').directive 'dialog', ($http, $log) ->
    return {
        restrict: 'E'
        transclude: true
        template: '''
            <div class="modal" ng:show="attrs.ngShow || attrs.ngIf">
                <div class="modal-dialog {{attrs.dialogClass}}">
                    <div class="modal-content">
                        <ng-transclude></ng-transclude>
                    </div>
                </div>
            </div>
        '''
        link: ($scope, element, attrs) ->
            element.addClass('block-element')
            $scope.attrs = attrs
            $scope.$watch 'attrs.ngShow', () ->
                if attrs.ngShow
                    setTimeout () ->
                        element.find('*[autofocus]').focus()
    }
    