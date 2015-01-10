angular.module('core').factory 'unauthenticatedInterceptor', ($q, $rootScope, $location, notify, urlPrefix) ->
    return {
        responseError: (rejection) ->
            if $rootScope.disableExpiredSessionInterceptor or $location.path().indexOf("#{urlPrefix}/view/login") == 0
                return $q.reject(rejection)

            if rejection and rejection.status == 401
                $rootScope.disableExpiredSessionInterceptor = true
                notify.error 'Your session has expired'
                location.assign("#{urlPrefix}/view/login/normal/#{$location.path()}")
                #identity.login() # circular dep - TODO

            return $q.reject(rejection)
    }


angular.module('core').factory 'urlPrefixInterceptor', ($q, $rootScope, $location, notify, urlPrefix) ->
    return {
        request: (config) ->
            config.url = urlPrefix + config.url
            return config
    }
