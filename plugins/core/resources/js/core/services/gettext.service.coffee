_ = {}

# angular-gettext defines a stub as a constant, impossible to override it with e.g. factory
angular.module('core').constant 'gettext', (str) -> _.gettextCatalog.getString(str)

angular.module('core').service 'locale', ($http, gettextCatalog) ->
    _.gettextCatalog = gettextCatalog

    @setLanguage = (lang) ->
        return $http.get("/resources/all.locale.js?lang=#{lang}").then (rq) ->
            gettextCatalog.setStrings(lang, rq.data)
            gettextCatalog.setCurrentLanguage(lang) 

    return this 

angular.module('core').run (locale, config) ->
    config.promise.then () ->
        locale.setLanguage(config.data.language or 'en')

