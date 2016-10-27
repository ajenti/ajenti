angular.module('ajenti.power', [
    'core',
]);

angular.module('ajenti.power').run((customization) => {
    customization.plugins.power = {};
    customization.plugins.power.hideBatteries = false;
    customization.plugins.power.hideAdapters = false;
});
