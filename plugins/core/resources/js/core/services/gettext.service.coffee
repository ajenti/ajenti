angular.module('core').service 'gettext', (gettextCatalog) ->
    return (str) -> gettextCatalog.getString(str)

angular.module('core').service 'locale', ($http, gettextCatalog) ->
    @setLanguage = (lang) ->
        return $http.get("/resources/all.locale.js?lang=#{lang}").then (rq) ->
            gettextCatalog.setStrings(lang, rq.data)
            gettextCatalog.setCurrentLanguage(lang) 

    return this 

angular.module('core').run (locale, config) ->
    config.promise.then () ->
        locale.setLanguage(config.data.language or 'en')

