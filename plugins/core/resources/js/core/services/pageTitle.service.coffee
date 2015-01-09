angular.module('core').service 'pageTitle', ($rootScope) ->
    @set = (expr, scope) ->
        if not scope
            scope = $rootScope
            expr = "'#{expr}'"
        refresh = () ->
            title = scope.$eval(expr)
            if angular.isDefined(title)
                $rootScope.pageTitle = title
        scope.$watch expr, () ->
            refresh()
        refresh()

    return this

