angular.module('core').directive 'rootAccess', (identity) ->
    return {
        restrict: 'A'
        link: ($scope, element, attr) ->
            template = """
                <div class="text-center root-access-blocker">
                    <h1>
                        <i class="fa fa-lock"></i>
                    </h1>
                    <h3>
                        Superuser access required
                    </h3>
                </div>
            """
            identity.promise.then () ->
                if not identity.isSuperuser
                    element.empty().append($(template))
    }
