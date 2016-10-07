let _ = {};

// angular-gettext defines a stub as a constant, impossible to override it with e.g. factory
angular.module('core').constant('gettext', str => _.gettextCatalog.getString(str));

angular.module('core').service('locale', function($http, gettextCatalog) {
    _.gettextCatalog = gettextCatalog;

    this.setLanguage = lang =>
        $http.get(`/resources/all.locale.js?lang=${lang}`).then(function(rq) {
            gettextCatalog.setStrings(lang, rq.data);
            return gettextCatalog.setCurrentLanguage(lang);
        })
    ;

    return this;
});

angular.module('core').run((locale, config) =>
    config.promise.then(() => locale.setLanguage(config.data.language || 'en'))
);
