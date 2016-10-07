angular.module('core').directive('dialog', ($http, $log, $timeout) =>
    ({
        restrict: 'E',
        transclude: true,
        template: `
            <div class="modal">
                <div class="modal-dialog {{attrs.dialogClass}}">
                    <div class="modal-content">
                        <ng-transclude></ng-transclude>
                    </div>
                </div>
            </div>`,
        link($scope, element, attrs) {
            element.addClass('block-element');
            $timeout(() => element.addClass('animate-modal'));

            $scope.attrs = attrs;
            $scope.$watch('attrs.ngShow', () => {
                if (attrs.ngShow) {
                    return setTimeout(() => element.find('*[autofocus]').focus());
                }
            });
        }
    })
);
