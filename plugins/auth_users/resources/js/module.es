angular.module('ajenti.auth.users', [
    'core',
]);

angular.module('ajenti.auth.users').run((customization) => {
    customization.plugins.auth_users = {
        forceUID: null
    };
});
