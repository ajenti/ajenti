angular.module('core').service 'gettext', (gettextCatalog) ->
    return (str) -> gettextCatalog.getString(str)
