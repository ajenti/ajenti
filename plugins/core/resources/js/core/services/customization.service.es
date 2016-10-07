angular.module('core').service('customization', function() {
    this.plugins = {core: {
        extraProfileMenuItems: []
    }};
    return this;
});
