angular.module('core').directive('floatingToolbar', () =>
    ({
        restrict: 'E',
        transclude: true,
        template: `
            <div class="container">
                <div class="row">
                    <div ng:class="{'col-md-3': showSidebar}">
                    </div>
                    <div ng:class="{'col-md-9': showSidebar, 'col-md-12': !showSidebar}">
                        <div class="bar row">
                            <ng-transclude></ng-transclude>
                        </div>
                    </div>
                </div>
            </div>`
    })
);
