angular.module('core').directive('autofocus', ($timeout) => {
    return {
        restrict: 'A',
        link(scope, element) {
            $timeout(() => element[0].focus());
        }
    }
});
