angular.module('core').directive 'floatingToolbar', () ->
    return {
        restrict: 'E'
        transclude: true
        template: '''
            <div class="container">
                <div class="row">
                    <div class="col-lg-3">
                    </div>
                    <div class="col-lg-9">
                        <div class="bar row">
                            <ng-transclude></ng-transclude>
                        </div>
                    </div>
                </div>
            </div>
        '''
        link: ($scope, element, attrs) ->
    }
    