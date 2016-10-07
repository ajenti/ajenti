angular.module('core').controller('CoreIndexController', function($scope, $location, customization, identity, urlPrefix) {
    $location.path(customization.plugins.core.startupURL || '/view/dashboard');

    identity.promise.then(() => {
        if (!identity.user) {
            location.assign(`${urlPrefix}/view/login/normal`);
        }
    });
});
