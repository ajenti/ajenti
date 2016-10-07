angular.module('core').directive('progressSpinner', () =>
    ({
        restrict: 'E',
        template: `
            <div>
                <div class="one"></div>
                <div class="two"></div>
            </div>`,
    })
);
