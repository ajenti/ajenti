angular.module('ajenti.settings', [
    'core',
    'ajenti.filesystem',
    'ajenti.passwd',
]);

angular.module('ajenti.settings').run(customization =>
    customization.plugins.settings = {}
);
