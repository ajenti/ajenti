angular.module('core').service('pageTitle', function($rootScope) {
    this.set = (expr, scope) => {
        if (!scope) {
            $rootScope.pageTitle = expr;
        } else {
            let refresh = () => {
                let title = scope.$eval(expr);
                if (angular.isDefined(title)) {
                    $rootScope.pageTitle = title;
                }
            };

            scope.$watch(expr, () => refresh());
            refresh();
        }
    };

    return this;
});
